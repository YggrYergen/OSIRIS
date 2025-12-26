import logging
import json
from typing import Optional, Dict
from sqlalchemy import select
from app.services.brain.factory import BrainFactory, BrainProvider
from app.services.tools.registry import registry
from app.core.event_bus import event_bus
from app.schemas.events import EventArtifact, EventLog, EventMessage, EventType
from app.db.session import AsyncSessionLocal
from app.models.message import Message

# Setup Logger
logger = logging.getLogger("agent_service")

class AgentService:
    def __init__(self, task_id: int, provider: BrainProvider = BrainProvider.OPENAI, model: str = None):
        self.task_id = task_id
        # Pass model to BrainFactory
        self.brain = BrainFactory.get_brain(provider, model=model)
        self.logger = logger.getChild(f"task_{task_id}")

    async def load_history(self):
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Message).where(Message.task_id == self.task_id).order_by(Message.timestamp)
            )
            messages = result.scalars().all()
            history = []
            for m in messages:
                role = "user"
                if m.sender_type == "agent" or m.sender_type == "assistant":
                    role = "assistant"
                elif m.sender_type == "system":
                    role = "system"
                
                history.append({"role": role, "content": m.content})
            return history

    async def run_step(self, user_input: str = None, history: list = None):
        """
        Executes a singe turn of the agent loop.
        If user_input is provided, it's appended to history (or history starts with it).
        If user_input is None, we assume the latest message in context is the prompt.
        """
        if history is None:
            # If no manual history provided, load from DB
            history = await self.load_history()
        
        if user_input:
            history.append({"role": "user", "content": user_input})
            self.logger.info(f"Step Start: Input='{user_input}'")
        else:
            self.logger.info("Step Start: Responding to existing history")

        # Inject System Context (OS) if not present
        if not any(m["role"] == "system" for m in history):
            import sys
            os_name = "Windows" if sys.platform == "win32" else "Linux/Mac"
            system_msg = f"You are an AI Agent running on {os_name}. workspace_root=d:\\OSIRIS. Do NOT use /tmp or linux paths. Use relative paths or {os_name} paths."
            history.insert(0, {"role": "system", "content": system_msg})

        # 1. THINK
        try:
            decision = await self.brain.think(history, tools=registry.schemas)
        except Exception as e:
            self.logger.critical(f"Brain failure: {e}")
            await event_bus.publish(EventMessage(
                type=EventType.SYSTEM_ALERT,
                task_id=self.task_id,
                data={"message": f"Critical Brain Error: {str(e)}"}
            ))
            return

        content = decision.get("content")
        tool_calls = decision.get("tool_calls")

        # Notify Thought
        if content:
            self.logger.info(f"Agent Thought: {content}")
            history.append({"role": "assistant", "content": content})
            
            # Persist Thought to DB
            try:
                async with AsyncSessionLocal() as session:
                    msg = Message(
                        task_id=self.task_id,
                        content=content,
                        sender_type="agent"
                    )
                    session.add(msg)
                    await session.commit()
            except Exception as db_err:
                self.logger.error(f"Failed to persist agent message: {db_err}")

            # Stream Thought to Frontend
            await event_bus.publish(EventMessage(
                task_id=self.task_id,
                data={"content": content, "sender": "agent", "sender_type": "agent"}
            ))

        # 2. ACT
        if tool_calls:
            self.logger.info(f"Agent decided to use tools: {len(tool_calls)} calls")
            
            for call in tool_calls:
                func_name = call["function"]
                args = call["arguments"]
                call_id = call["id"]
                
                tool = registry.get_tool(func_name)
                if not tool:
                    self.logger.error(f"Tool not found: {func_name}")
                    result = f"Error: Tool {func_name} not found."
                else:
                    self.logger.debug(f"Executing {func_name} with {args}")
                    
                    # Notify intention
                    await event_bus.publish(EventLog(
                        task_id=self.task_id,
                        data={"command": f"Running {func_name}", "output": "..."}
                    ))
                    
                    try:
                        result = tool(**args)
                    except Exception as te:
                        result = f"Error executing tool: {te}"
                        self.logger.error(f"Tool execution failed: {te}")
                
                # Notify Result
                self.logger.info(f"Tool Output: {result}")
                
                 # Special handling for artifacts to show visualization
                if func_name in ["write_file", "read_file"]:
                    path = args.get("path")
                    if "write" in func_name:
                         await event_bus.publish(EventArtifact(
                            task_id=self.task_id,
                            data={"filename": path, "content": args.get("content")}
                        ))

                await event_bus.publish(EventLog(
                     task_id=self.task_id,
                     data={"command": func_name, "output": str(result)[:500]} # Truncate log
                ))
                
                # Update History for next turn
                history.append({
                    "role": "tool",
                    "tool_call_id": call_id,
                    "content": str(result)
                })
                
            # Recursive / Follow-up thought (The Brain should see the tool output and respond)
            # For simplicity in this step, we just finish, but in real loop we'd recurse.

import logging
import json
from typing import Optional, Dict
from app.services.brain.factory import BrainFactory, BrainProvider
from app.services.tools.registry import registry
from app.core.event_bus import event_bus
from app.schemas.events import EventArtifact, EventLog, EventMessage, EventType
from app.db.session import AsyncSessionLocal
from app.models.message import Message

# Setup Logger
logger = logging.getLogger("agent_service")

class AgentService:
    def __init__(self, task_id: int, provider: BrainProvider = BrainProvider.OPENAI):
        self.task_id = task_id
        self.brain = BrainFactory.get_brain(provider)
        self.logger = logger.getChild(f"task_{task_id}")

    async def run_step(self, user_input: str, history: list = None):
        """
        Executes a single turn of the agent loop.
        1. Think (Call LLM)
        2. Act (Execute Tools)
        3. Notify (SSE)
        """
        if history is None:
            history = []
        
        # Add User Message
        history.append({"role": "user", "content": user_input})
        self.logger.info(f"Step Start: Input='{user_input}'")

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

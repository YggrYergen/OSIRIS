import os
import sys
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource, Resource
import mcp.types as types
from dotenv import load_dotenv

# Add backend to path to reuse DB models and config
# Assumes we are running from root or mcp-server directory
sys.path.append(os.path.join(os.path.dirname(__file__), "../../backend"))

try:
    from app.core.config import settings
    from app.db.session import AsyncSessionLocal
    from app.models.task import Task, TaskStatus, TaskSource
    from app.models.artifact import Artifact, ArtifactType, ArtifactStatus
    from app.models.message import Message, SenderType
    from sqlalchemy import select, update
except ImportError:
    # Fallback/Mock for development if backend is not found
    print("Backend modules not found. Ensure you run this from the correct context.")
    sys.exit(1)

# Initialize MCP Server
app = Server("osiris-orchestrator")

# ------------------------------------------------------------------------------
# DATABASE HELPERS
# ------------------------------------------------------------------------------
async def get_pending_tasks_from_db():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Task).where(Task.status == TaskStatus.PENDING)
        )
        tasks = result.scalars().all()
        return [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "source": t.source,
                "created_at": t.created_at.isoformat() if t.created_at else None
            }
            for t in tasks
        ]

async def claim_task_in_db(task_id: int):
    async with AsyncSessionLocal() as session:
        # Check if task exists and is pending
        result = await session.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        
        if not task:
            raise ValueError(f"Task {task_id} not found")
        if task.status != TaskStatus.PENDING:
            raise ValueError(f"Task {task_id} is not pending (Status: {task.status})")
            
        task.status = TaskStatus.CLAIMED
        # In a real scenario, we would assign the agent user ID here
        # task.assigned_to = ... 
        
        await session.commit()
        return task

async def submit_artifact_in_db(task_id: int, content: str, msg_type: str):
    async with AsyncSessionLocal() as session:
        # Verify task
        result = await session.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        if not task:
            raise ValueError(f"Task {task_id} not found")
            
        # Create Artifact
        artifact = Artifact(
            task_id=task_id,
            type=msg_type, # code, text, etc
            content=content,
            status=ArtifactStatus.PENDING
        )
        session.add(artifact)
        
        # Update Task Status
        task.status = TaskStatus.REVIEW_PENDING
        
        await session.commit()
        return artifact

async def send_message_in_db(task_id: int, text: str):
    async with AsyncSessionLocal() as session:
        msg = Message(
            task_id=task_id,
            sender_type=SenderType.AGENT,
            content=text
        )
        session.add(msg)
        await session.commit()
        return msg

# ------------------------------------------------------------------------------
# RESOURCES
# ------------------------------------------------------------------------------
@app.list_resources()
async def list_resources():
    return [
        Resource(
            uri="orchestrator://queue",
            name="Task Queue",
            mimeType="application/json",
            description="List of pending tasks waiting for assignment"
        )
    ]

@app.read_resource()
async def read_resource(uri: str):
    if uri == "orchestrator://queue":
        tasks = await get_pending_tasks_from_db()
        return str(tasks)
    raise ValueError(f"Resource not found: {uri}")

# ------------------------------------------------------------------------------
# TOOLS
# ------------------------------------------------------------------------------
@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="claim_ticket",
            description="Claim a pending task to start working on it.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "ID of the task to claim"}
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="submit_artifact",
            description="Submit work (code, plan, screenshot) for human review.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"},
                    "content": {"type": "string", "description": "The content or file path of the artifact"},
                    "type": {"type": "string", "enum": ["code", "text", "screenshot"], "description": "Type of artifact"}
                },
                "required": ["task_id", "content", "type"]
            }
        ),
        Tool(
            name="send_message",
            description="Send a message to the task chat (visible to user/supervisor).",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"},
                    "text": {"type": "string"}
                },
                "required": ["task_id", "text"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "claim_ticket":
        task_id = arguments.get("task_id")
        try:
            await claim_task_in_db(task_id)
            return [TextContent(type="text", text=f"Successfully claimed task {task_id}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error claiming task: {str(e)}")]
            
    elif name == "submit_artifact":
        try:
            await submit_artifact_in_db(
                arguments.get("task_id"), 
                arguments.get("content"), 
                arguments.get("type")
            )
            return [TextContent(type="text", text="Artifact submitted for review.")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error submitting artifact: {str(e)}")]

    elif name == "send_message":
        try:
            await send_message_in_db(arguments.get("task_id"), arguments.get("text"))
            return [TextContent(type="text", text="Message sent.")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error sending message: {str(e)}")]

    raise ValueError(f"Tool not found: {name}")

# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    if hasattr(asyncio, "run"):
        asyncio.run(main())
    else:
        # Python < 3.7 legacy
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())

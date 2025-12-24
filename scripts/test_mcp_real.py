import sys
import os
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock

# Add paths
sys.path.append(os.path.join(os.getcwd(), 'backend'))
sys.path.append(os.path.join(os.getcwd(), 'mcp-server/src'))

from app.core.logging_config import setup_logging, log
# Import base to register all models (User, Task, etc)
from app.db.base import Base
from app.models.task import Task, TaskStatus

# REAL TESTING SCRIPT
# This script will attempt to connect to the REAL database and execute the logic
# To verify it ACTUALLY works and updates the Dashboard.

# We need to import the actual function from server.py (which uses AsyncSessionLocal)
# But we need to make sure AsyncSessionLocal points to the real DB file.
# The server.py imports AsyncSessionLocal from app.db.session, which uses env vars.
# We must ensure env vars are set correctly before import or rely on .env loading.

async def main():
    setup_logging("INFO")
    log.info("Starting MCP Logic verification (LIVE DB)")
    
    # Check if DB file exists
    db_path = os.path.join(os.getcwd(), 'backend', 'osiris_demo.db')
    if not os.path.exists(db_path):
        log.error(f"DB File not found at {db_path}")
        return

    # Assuming env vars are loaded by app.core.config inside server.py
    # Let's import the server logic
    try:
        from server import claim_task_in_db, get_pending_tasks_from_db
    except ImportError as e:
        log.error(f"Failed to import server module: {e}")
        return

    try:
        # 1. List Pending Tasks
        log.info("Fetching pending tasks...")
        tasks = await get_pending_tasks_from_db()
        log.info(f"Pending tasks found: {len(tasks)}")
        
        if not tasks:
            log.warning("No pending tasks to claim! Please run inject_task.py first.")
            return

        target_task = tasks[0]
        t_id = target_task['id']
        log.info(f"Attempting to claim Task #{t_id}: {target_task['title']}")

        # 2. Claim Task
        updated_task = await claim_task_in_db(t_id)
        log.success(f"Task #{updated_task.id} claimed! Status: {updated_task.status}")

        if updated_task.status == TaskStatus.CLAIMED:
            log.success("VERIFICATION SUCCESSFUL: Task status updated in DB.")
            log.info("Please refresh the dashboard to see the change.")
        else:
            log.error(f"Verification Failed. Status is {updated_task.status}")

    except Exception as e:
        log.exception(f"MCP Test Failed: {e}")

if __name__ == "__main__":
    # Ensure asyncio uses the right loop policy on Windows
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())

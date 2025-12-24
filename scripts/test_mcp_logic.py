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

# Mock DB Session for MCP
# We need to patch AsyncSessionLocal inside server.py
# This is tricky without dependency injection, but we will patch the module

def mock_execute_result():
    t = Task(id=1, title="MCP Task", description="Testing MCP", status=TaskStatus.PENDING)
    mock_result = MagicMock()
    # scalar_one_or_none is synchronous on the result object
    mock_result.scalar_one_or_none.return_value = t
    return mock_result

async def main():
    setup_logging("INFO")
    log.add("verification.log", level="INFO")
    log.info("Starting MCP Logic verification")
    
    with patch('server.AsyncSessionLocal') as MockSession:
        # Configurar el mock de la sesión
        mock_session_instance = AsyncMock() # Main session is async mock
        # __aenter__ and __aexit__ are handled by AsyncMock usually but let's be explicit if needed
        mock_session_instance.__aenter__.return_value = mock_session_instance
        mock_session_instance.__aexit__.return_value = None
        
        MockSession.return_value = mock_session_instance
        
        # Mock execute returning a Task
        mock_session_instance.execute.return_value = mock_execute_result()
        # commit is already async because AsyncMock
        
        # Import target functions now that patch is ready (if they bind at runtime, otherwise patch where imported)
        # Since server.py imports at top level, we might rely on the patch being active when we call the function
        from server import claim_task_in_db
        
        try:
            log.info("Testing claim_ticket logic...")
            task = await claim_task_in_db(1)
            
            assert task.status == TaskStatus.CLAIMED
            # Verify commit was called
            mock_session_instance.commit.assert_called_once()
            
            log.success("MCP Claim Ticket Logic Verified!")
            
        except Exception as e:
            log.exception(f"MCP Test Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())

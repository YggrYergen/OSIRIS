# FIX PLAN: Robust Chat & Agent Integration

## Problem Diagnosis
The user reports that the chat allows only one message and then stops working. This suggests the WebSocket connection is crashing or hanging after the first message processing.

Potential causes:
1.  **Sync within Async**: The `AgentService` instantiation might be blocking or raising an unhandled exception inside the WS loop.
2.  **Concurrency Issue**: Database session usage inside the loop might be conflicting.
3.  **Agent Crash**: Since API keys are missing, `AgentService` might fail during `__init__` (Brain instantiation), crashing the WS handler.

## Proposed Solution

### 1. Robust Error Handling in WebSocket Endpoint
Wrap the "Trigger Agent" logic in a broad `try/except` block to ensure the WS loop *never* exits due to agent errors.

### 2. Lazy Agent Instantiation
Ensure `AgentService` initialization handles missing keys gracefully or defers checks until `run_step`.

### 3. Frontend Chat UX
Verify `ChatInterface` isn't blocking input while waiting for a response that might never come (if agent fails silently).

## Steps

1.  **Modify `backend/app/api/api.py`**:
    - Wrap agent triggering in a dedicated function or safe block.
    - Log errors explicitly without re-raising.

2.  **Verify `AgentService.__init__`**:
    - Ensure `BrainFactory` doesn't crash if keys are None (it should probably log a warning but instantiate a "DummyBrain" or fail gracefully later).

3.  **Frontend Feedback**:
    - Ensure UI shows if socket disconnects.

4.  **Verification**:
    - Start server.
    - Send multiple messages quickly.
    - Verify they are echo'd back.
    - Verify logs show agent failure (due to missing keys) but NOT server crash.

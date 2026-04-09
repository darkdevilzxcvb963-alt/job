from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from app.core.socket_manager import manager
from app.core.security import verify_token
from loguru import logger

router = APIRouter()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    token: str = Query(...)
):
    """
    WebSocket endpoint for real-time notifications and messaging.
    Auth is handled via token query parameter because WebSockets don't support custom headers easily.
    """
    try:
        # Verify token
        payload = verify_token(token)
        token_user_id = payload.get("sub")
        
        if str(token_user_id) != str(user_id):
            logger.warning(f"WebSocket auth failed: User ID mismatch. {token_user_id} != {user_id}")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Connect user
        await manager.connect(user_id, websocket)
        
        try:
            while True:
                # We mainly use this for receiving (pings/etc), 
                # but most logic is server -> client push.
                data = await websocket.receive_text()
                # If we want to handle client-side commands, we check 'data' here.
                # For now, just a heartbeat or "seen" acknowledgement.
                pass
        except WebSocketDisconnect:
            manager.disconnect(user_id, websocket)
        except Exception as e:
            logger.error(f"WebSocket error for user {user_id}: {e}")
            manager.disconnect(user_id, websocket)
            
    except Exception as e:
        logger.error(f"WebSocket connection failed for user {user_id}: {e}")
        # Invalid token or other error
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

from fastapi import WebSocket
from typing import Dict, List, Any
import json
from loguru import logger

class ConnectionManager:
    """Manages active WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Maps user_id to a list of active WebSocket connections
        # (A user might have multiple tabs open)
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        """Accept a new connection for a user"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"User {user_id} connected. Total active connections for user: {len(self.active_connections[user_id])}")

    def disconnect(self, user_id: str, websocket: WebSocket):
        """Remove a connection for a user"""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            logger.info(f"User {user_id} disconnected.")

    async def send_personal_message(self, message: str, user_id: str):
        """Send a string message to a specific user (all tabs)"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error sending text message to user {user_id}: {e}")

    async def send_json_to_user(self, data: Dict[str, Any], user_id: str):
        """Send a JSON payload to a specific user (all tabs)"""
        if user_id in self.active_connections:
            logger.debug(f"Sending real-time update to user {user_id}: {data.get('type')}")
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(data)
                except Exception as e:
                    logger.error(f"Error sending JSON to user {user_id}: {e}")

    async def broadcast(self, data: Dict[str, Any]):
        """Broadcast JSON payload to all connected users"""
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(data)
                except Exception as e:
                    logger.error(f"Error broadcasting to user {user_id}: {e}")

# Global instance
manager = ConnectionManager()

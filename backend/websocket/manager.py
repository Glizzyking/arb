import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Set
from fastapi import WebSocket

class WebSocketManager:
    """Manages frontend WebSocket connections and broadcasts data"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.latest_data: Dict[str, Dict[str, Any]] = {} # {asset: data}
        self.lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
    
    async def broadcast(self, data: Dict[str, Any]):
        """Update latest data and broadcast to all clients"""
        asset = data.get("asset", "unknown")
        async with self.lock:
            data["timestamp"] = datetime.now().isoformat()
            self.latest_data[asset] = data
        
        # Broadcast to all clients
        connections = list(self.active_connections)
        if not connections:
            return
            
        message = json.dumps(data)
        dead_connections = []
        
        for conn in connections:
            try:
                await conn.send_text(message)
            except Exception:
                dead_connections.append(conn)
        
        # Clean up dead connections
        for conn in dead_connections:
            self.active_connections.discard(conn)

# Global manager instance
ws_manager = WebSocketManager()

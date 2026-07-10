# backend/websocket_manager.py

import asyncio
import json
from typing import Any
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages active WebSocket connections with topic-based subscriptions.
    Topics: "shipments", "alerts", "shipment:{id}"
    """

    def __init__(self) -> None:
        # topic -> set of websockets
        self._connections: dict[str, set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, topic: str = "all") -> None:
        await websocket.accept()
        async with self._lock:
            if topic not in self._connections:
                self._connections[topic] = set()
            self._connections[topic].add(websocket)
        logger.info(f"[WS] Client connected to topic '{topic}'. Total: {self._total_connections()}")

    async def disconnect(self, websocket: WebSocket, topic: str = "all") -> None:
        async with self._lock:
            if topic in self._connections:
                self._connections[topic].discard(websocket)
        logger.info(f"[WS] Client disconnected from '{topic}'.")

    async def broadcast(self, topic: str, data: Any) -> None:
        """Broadcast to all clients subscribed to a topic."""
        message = json.dumps(data, default=str)
        dead_sockets = set()

        for ws in list(self._connections.get(topic, set())):
            try:
                await ws.send_text(message)
            except Exception:
                dead_sockets.add(ws)

        # Also broadcast to "all" subscribers
        if topic != "all":
            for ws in list(self._connections.get("all", set())):
                try:
                    await ws.send_text(message)
                except Exception:
                    dead_sockets.add(ws)

        # Cleanup dead connections
        async with self._lock:
            for t in self._connections:
                self._connections[t] -= dead_sockets

    async def send_personal(self, websocket: WebSocket, data: Any) -> None:
        try:
            await websocket.send_text(json.dumps(data, default=str))
        except Exception as e:
            logger.warning(f"[WS] Failed to send personal message: {e}")

    def _total_connections(self) -> int:
        return sum(len(v) for v in self._connections.values())

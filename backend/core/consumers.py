
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from core.in_memory_store import InMemoryStore
import logging
import threading
import asyncio

logger = logging.getLogger(__name__)

store = InMemoryStore()

# Create a thread-safe connection manager for our WebSocket consumers
class CoreConnectionManager:
    def __init__(self):
        self._connections = {}
        self._lock = threading.Lock()

    async def connect(self, channel_name, topic="all"):
        with self._lock:
            if topic not in self._connections:
                self._connections[topic] = set()
            self._connections[topic].add(channel_name)
        logger.info(f"[WS] Client {channel_name} connected to topic '{topic}'.")

    async def disconnect(self, channel_name, topic="all"):
        with self._lock:
            if topic in self._connections:
                self._connections[topic].discard(channel_name)
        logger.info(f"[WS] Client {channel_name} disconnected from '{topic}'.")

    async def broadcast(self, topic, data):
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        
        dead_channels = set()
        target_channels = set()
        with self._lock:
            if topic in self._connections:
                target_channels.update(self._connections[topic])
            # Also broadcast to all topic
            if topic != "all" and "all" in self._connections:
                target_channels.update(self._connections["all"])
            
        for channel_name in list(target_channels):
            try:
                await channel_layer.send(
                    channel_name,
                    {
                        "type": "send.message",
                        "message": data,
                    }
                )
            except Exception:
                dead_channels.add(channel_name)
        
        # Cleanup dead channels
        with self._lock:
            for t in self._connections:
                self._connections[t] -= dead_channels

manager = CoreConnectionManager()


class SupplyChainConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.topic = self.scope["url_route"]["kwargs"].get("topic", "all")
        await self.channel_layer.group_add(self.topic, self.channel_name)
        await manager.connect(self.channel_name, self.topic)
        await self.accept()
        
        # Send initial state to the new client
        if self.topic in ("all", "shipments"):
            shipments = await database_sync_to_async(store.get_all_active_shipments)()
            await self.send(text_data=json.dumps({
                "event": "initial_state",
                "shipments": shipments
            }, default=str))

    async def disconnect(self, close_code):
        await manager.disconnect(self.channel_name, self.topic)
        await self.channel_layer.group_discard(self.topic, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json == "ping" or text_data_json.get("type") == "ping":
            await self.send(text_data=json.dumps({"event": "pong"}))

    async def send_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps(message, default=str))

# Background task to poll the in-memory store and broadcast updates
async def store_change_poller():
    last_snapshot = {}
    while True:
        try:
            shipments = await database_sync_to_async(store.get_all_active_shipments)()
            changes = []
            for s in shipments:
                sid = s["id"]
                old = last_snapshot.get(sid, {})
                if (old.get("risk_score") != s.get("risk_score") or
                    old.get("status") != s.get("status") or
                    old.get("is_anomaly") != s.get("is_anomaly")):
                    changes.append(s)
                last_snapshot[sid] = s

            if changes:
                await manager.broadcast("shipments", {
                    "event": "shipments_updated",
                    "data": changes
                })

        except Exception as e:
            logger.warning(f"[Poller] Error: {e}")

        await asyncio.sleep(3)

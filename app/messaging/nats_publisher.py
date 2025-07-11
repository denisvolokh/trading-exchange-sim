import json
import asyncio
from nats.aio.client import Client as NATS

NATS_URL = "nats://nats:4222"

_lock = asyncio.Lock()
_client_ref: dict[str, NATS] = {}

async def get_nats_client() -> NATS:
    async with _lock:
        if "client" not in _client_ref or not _client_ref["client"].is_connected:
            client = NATS()
            await client.connect(servers=["nats://nats:4222"])
            _client_ref["client"] = client
        return _client_ref["client"]

async def publish_event(subject: str, payload: dict):
    client = await get_nats_client()
    await client.publish(subject, json.dumps(payload).encode("utf-8"))

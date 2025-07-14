import asyncio
import json
from sse_starlette.sse import EventSourceResponse
from fastapi import Request

clients = []

async def broadcast_sse_event(event_type: str, data: dict):
    msg = json.dumps({
        "type": event_type,
        "data": data
    })
    print(f"[broadcast_sse_event] Sending: {msg}, Clients: {len(clients)}")

    for q in clients:
        await q.put(msg)


async def sse_endpoint(request):
    async def event_generator():
        q = asyncio.Queue()
        clients.append(q)
        try:
            while True:
                msg = await q.get()
                yield msg
        except asyncio.CancelledError:
            clients.remove(q)
            raise

    return EventSourceResponse(event_generator())

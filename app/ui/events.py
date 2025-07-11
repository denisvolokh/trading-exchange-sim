import asyncio
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from nats.aio.client import Client as NATS

sse_router = APIRouter()
event_queue = asyncio.Queue()

async def handle_event(msg):
    await event_queue.put("data: update\n\n")

@sse_router.get("/sse")
async def sse():
    async def event_generator():
        while True:
            msg = await event_queue.get()
            yield msg

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# Background task to subscribe to NATS
async def start_nats_listener():
    nc = NATS()
    await nc.connect(servers=["nats://nats:4222"])
    await nc.subscribe("OrderPlaced.v1", cb=handle_event)
    await nc.subscribe("OrderMatched.v1", cb=handle_event)
    await nc.subscribe("OrderCancelled.v1", cb=handle_event)

# Trigger on startup
@sse_router.on_event("startup")
async def on_startup():
    asyncio.create_task(start_nats_listener())

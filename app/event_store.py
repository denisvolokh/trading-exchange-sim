import json
from app.models import EventStore
from app.messaging.nats_publisher import publish_event
from sqlalchemy.ext.asyncio import AsyncSession

async def append_event(
    db: AsyncSession,
    event_type: str,
    version: int,
    payload: dict
) -> EventStore:
    event = EventStore(
        event_type=event_type,
        version=version,
        payload=json.dumps(payload)
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)

    await publish_event(f"{event_type}.v{version}", payload)
    return event

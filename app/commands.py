from sqlalchemy.ext.asyncio import AsyncSession
from app.event_store import append_event
from app.models import OrderProjection, OrderSide
from app.domain_events import OrderPlacedV1, OrderCancelledV1
from app.projections import apply_event_to_order_book, apply_event_to_trades
from app.matching_engine import try_match_order
from app.schemas import OrderCreateRequest
from app.sse import broadcast_sse_event

async def place_order_command(db: AsyncSession, order: OrderCreateRequest):
    event = OrderPlacedV1(
        order_id=order.order_id,
        side=order.side,
        price=order.price,
        quantity=order.quantity,
        version=1
    )
    saved_event = await append_event(db, "OrderPlaced", event.version, event.dict())
    await apply_event_to_order_book(db, saved_event.event_type, saved_event.payload)

    # Notify clients about new order
    await broadcast_sse_event("order", {"order_id": order.order_id})

    await try_match_order(db, order.order_id)

    return {"status": "placed", "order_id": order.order_id}

async def cancel_order_command(db: AsyncSession, order_id: int):
    event = OrderCancelledV1(order_id=order_id, version=1)
    saved_event = await append_event(db, "OrderCancelled", event.version, event.dict())
    await apply_event_to_order_book(db, saved_event.event_type, saved_event.payload)

    # Notify clients about order cancellation
    await broadcast_sse_event("order", {"order_id": order_id})

    return {"status": "cancelled", "order_id": order_id}

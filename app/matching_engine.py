import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import OrderProjection, OrderSide
from app.event_store import append_event
from app.domain_events import OrderMatchedV1
from app.projections import apply_event_to_order_book, apply_event_to_trades
from app.sse import broadcast_sse_event

async def try_match_order(db: AsyncSession, new_order_id: int):
    # Get the new order that was just placed
    result = await db.execute(
        select(OrderProjection).where(OrderProjection.order_id == new_order_id)
    )
    new_order = result.scalar_one_or_none()

    if not new_order or not new_order.is_active:
        return  # nothing to match

    # Determine opposing side
    opposing_side = OrderSide.SELL if new_order.side == OrderSide.BUY else OrderSide.BUY

    # Get matching candidates (sorted by price priority, then order_id as FIFO)
    candidates = await db.execute(
        select(OrderProjection)
        .where(OrderProjection.side == opposing_side)
        .where(OrderProjection.is_active.is_(True))
        .order_by(OrderProjection.price.asc() if opposing_side == OrderSide.SELL else OrderProjection.price.desc())
    )
    matches = candidates.scalars().all()

    for match_order in matches:
        # Price match check
        if new_order.side == OrderSide.BUY and new_order.price < match_order.price:
            break
        if new_order.side == OrderSide.SELL and new_order.price > match_order.price:
            break

        # Quantity to trade
        traded_qty = min(new_order.quantity, match_order.quantity)

        # Emit OrderMatched event
        match_event = OrderMatchedV1(
            buy_order_id=new_order.order_id if new_order.side == OrderSide.BUY else match_order.order_id,
            sell_order_id=new_order.order_id if new_order.side == OrderSide.SELL else match_order.order_id,
            price=match_order.price,
            quantity=traded_qty,
            side=new_order.side,
            version=1
        )
        saved_event = await append_event(db, "OrderMatched", match_event.version, match_event.dict())

        # Apply trade to projections
        await apply_event_to_trades(db, saved_event.event_type, saved_event.payload)

        # Broadcast trade update via SSE
        await broadcast_sse_event("trade", {
            "buy_order_id": match_event.buy_order_id,
            "sell_order_id": match_event.sell_order_id,
            "price": match_event.price,
            "quantity": match_event.quantity,
            "side": match_event.side,
        })

        # Update quantities in memory
        new_order.quantity -= traded_qty
        match_order.quantity -= traded_qty

        if match_order.quantity <= 0:
            match_order.is_active = False
        if new_order.quantity <= 0:
            new_order.is_active = False
            break  # fully filled

    await db.commit()

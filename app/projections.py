import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import OrderProjection, TradeProjection, OrderSide
from app.domain_events import OrderPlacedV1, OrderCancelledV1, OrderMatchedV1

async def apply_event_to_order_book(db: AsyncSession, event_type: str, payload_json: str):
    payload = json.loads(payload_json)

    if event_type.startswith("OrderPlaced"):
        event = OrderPlacedV1(**payload)
        order = OrderProjection(
            order_id=event.order_id,
            price=event.price,
            quantity=event.quantity,
            side=event.side,
            is_active=True
        )
        db.add(order)

    elif event_type.startswith("OrderCancelled"):
        event = OrderCancelledV1(**payload)
        result = await db.execute(
            select(OrderProjection).where(OrderProjection.order_id == event.order_id)
        )
        order = result.scalar_one_or_none()
        if order:
            order.is_active = False

    await db.commit()

async def apply_event_to_trades(db: AsyncSession, event_type: str, payload_json: str):
    payload = json.loads(payload_json)

    if event_type.startswith("OrderMatched"):
        event = OrderMatchedV1(**payload)
        trade = TradeProjection(
            buy_order_id=event.buy_order_id,
            sell_order_id=event.sell_order_id,
            price=event.price,
            quantity=event.quantity,
            side=event.side,
        )
        db.add(trade)

        # Update order quantities or deactivate if filled
        for order_id in [event.buy_order_id, event.sell_order_id]:
            result = await db.execute(
                select(OrderProjection).where(OrderProjection.order_id == order_id)
            )
            order = result.scalar_one_or_none()
            if order:
                if order.quantity > event.quantity:
                    order.quantity -= event.quantity
                else:
                    order.is_active = False

    await db.commit()

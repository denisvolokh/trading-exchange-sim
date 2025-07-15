from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import OrderProjection, OrderSide, TradeProjection
from app.schemas import OrderBookEntry, TradeEntry


async def get_order_book(db: AsyncSession) -> dict[str, list[OrderBookEntry]]:
    result = await db.execute(
        select(OrderProjection).where(OrderProjection.is_active.is_(True))
    )
    orders = result.scalars().all()

    bids = [
        OrderBookEntry(order_id=o.order_id, price=o.price, quantity=o.quantity)
        for o in orders
        if o.side == OrderSide.BUY
    ]
    asks = [
        OrderBookEntry(order_id=o.order_id, price=o.price, quantity=o.quantity)
        for o in orders
        if o.side == OrderSide.SELL
    ]

    # Optionally: sort for display
    bids.sort(key=lambda o: o.price, reverse=True)
    asks.sort(key=lambda o: o.price)

    return {"bids": bids, "asks": asks}


async def get_recent_trades(db: AsyncSession) -> list[TradeEntry]:
    result = await db.execute(
        select(TradeProjection).order_by(TradeProjection.timestamp.desc()).limit(50)
    )
    trades = result.scalars().all()

    return [
        TradeEntry(
            buy_order_id=t.buy_order_id,
            sell_order_id=t.sell_order_id,
            price=t.price,
            quantity=t.quantity,
            side=t.side,
            timestamp=t.timestamp,
        )
        for t in trades
    ]

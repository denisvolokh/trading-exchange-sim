from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import OrderProjection, OrderSide, TradeProjection
from app.schemas import TradeEntry


async def get_order_book(db: AsyncSession):
    result = await db.execute(
        select(
            OrderProjection.side,
            OrderProjection.price,
            func.sum(OrderProjection.quantity).label("total_quantity")
        )
        .where(OrderProjection.is_active.is_(True))
        .group_by(OrderProjection.side, OrderProjection.price)
        .order_by(OrderProjection.side, OrderProjection.price.desc())
    )

    bids = []
    asks = []

    for side, price, total_quantity in result:
        entry = {"price": float(price), "quantity": float(total_quantity)}
        if side == OrderSide.BUY:
            bids.append(entry)
        else:
            asks.append(entry)

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

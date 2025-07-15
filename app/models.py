import enum

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.sql import func

from app.database import Base


class OrderSide(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"


class EventStore(Base):
    __tablename__ = "event_store"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, index=True)
    version = Column(Integer)
    payload = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class OrderProjection(Base):
    __tablename__ = "order_book"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, unique=True, index=True)
    side = Column(SqlEnum(OrderSide), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)


class TradeProjection(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True)
    buy_order_id = Column(Integer, nullable=False)
    sell_order_id = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    side = Column(SqlEnum(OrderSide), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

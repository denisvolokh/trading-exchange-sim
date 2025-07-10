from pydantic import BaseModel
from enum import Enum

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class VersionedEvent(BaseModel):
    version: int

class OrderPlacedV1(VersionedEvent):
    order_id: int
    price: float
    quantity: float
    side: OrderSide

    class Config:
        schema_extra = {"event_type": "OrderPlaced", "version": 1}

class OrderCancelledV1(VersionedEvent):
    order_id: int

    class Config:
        schema_extra = {"event_type": "OrderCancelled", "version": 1}

class OrderMatchedV1(VersionedEvent):
    buy_order_id: int
    sell_order_id: int
    price: float
    quantity: float

    class Config:
        schema_extra = {"event_type": "OrderMatched", "version": 1}

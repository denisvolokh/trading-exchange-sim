from pydantic import BaseModel
from app.models import OrderSide

class OrderCreateRequest(BaseModel):
    order_id: int
    side: OrderSide
    price: float
    quantity: float

class OrderBookEntry(BaseModel):
    order_id: int
    price: float
    quantity: float

class TradeEntry(BaseModel):
    buy_order_id: int
    sell_order_id: int
    price: float
    quantity: float

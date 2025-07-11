from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import engine, Base, get_db
from app.schemas import OrderCreateRequest, OrderBookEntry, TradeEntry
from app.commands import place_order_command, cancel_order_command
from app.queries import get_order_book, get_recent_trades
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from app.ui.views import ui_router
from app.ui.events import sse_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(ui_router)
app.include_router(sse_router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/orders")
async def place_order(request: OrderCreateRequest, db: AsyncSession = Depends(get_db)):
    return await place_order_command(db, request)

@app.post("/orders/{order_id}/cancel")
async def cancel_order(order_id: int, db: AsyncSession = Depends(get_db)):
    return await cancel_order_command(db, order_id)

@app.get("/orderbook", response_model=dict[str, list[OrderBookEntry]])
async def read_order_book(db: AsyncSession = Depends(get_db)):
    return await get_order_book(db)

@app.get("/trades", response_model=list[TradeEntry])
async def read_trades(db: AsyncSession = Depends(get_db)):
    return await get_recent_trades(db)

from uuid import uuid4

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse

from app.commands import place_order_command
from app.database import get_db
from app.queries import get_order_book, get_recent_trades
from app.schemas import OrderCreateRequest
from app.ui.dependencies import templates

ui_router = APIRouter()


@ui_router.get("/ui", response_class=HTMLResponse)
async def ui_page(request: Request):
    return templates.TemplateResponse("orderbook.html", {"request": request})


@ui_router.get("/ui/orderbook/asks", response_class=HTMLResponse)
async def ui_orderbook_asks(request: Request, db=Depends(get_db)):
    data = await get_order_book(db)
    return templates.TemplateResponse(
        "partials/orderbook_asks.html",
        {"request": request, "asks": data["asks"]},
    )


@ui_router.get("/ui/orderbook/bids", response_class=HTMLResponse)
async def ui_orderbook_bids(request: Request, db=Depends(get_db)):
    data = await get_order_book(db)
    return templates.TemplateResponse(
        "partials/orderbook_bids.html",
        {"request": request, "bids": data["bids"]},
    )


@ui_router.get("/ui/form", response_class=HTMLResponse)
async def ui_form(request: Request):
    return templates.TemplateResponse("partials/order_form.html", {"request": request})


@ui_router.post("/ui/order")
async def submit_order(
    request: Request,
    side: str = Form(...),
    price: float = Form(...),
    quantity: float = Form(...),
    db=Depends(get_db),
):
    if quantity > 999:
        return templates.TemplateResponse(
            "partials/order_failure.html",
            {
                "request": request,
                "error": "❌ Quantity must be 999 or less.",
                "side": side,
                "price": price,
                "quantity": quantity,
            },
            status_code=200,
        )

    order = OrderCreateRequest(
        order_id=int(uuid4().int >> 96), side=side, price=price, quantity=quantity
    )
    await place_order_command(db, order)

    return templates.TemplateResponse(
        "partials/order_success.html",
        {"request": request, "message": "✅ Order submitted!"},
        status_code=200,
    )


@ui_router.get("/ui/trades", response_class=HTMLResponse)
async def ui_trades(request: Request, db=Depends(get_db)):
    trades = await get_recent_trades(db)

    # Convert trades to dicts for the template
    trades_data = [
        {
            "side": "buy"
            if t.buy_order_id < t.sell_order_id
            else "sell",  # or use actual field if you store side
            "price": t.price,
            "quantity": t.quantity,
            "time": "just now",  # You can add timestamp formatting if needed
        }
        for t in trades
    ]
    return templates.TemplateResponse(
        "partials/trades.html", {"request": request, "trades": trades_data}
    )

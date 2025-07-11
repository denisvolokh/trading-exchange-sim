import pytest
import httpx

API_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_order_matching():
    async with httpx.AsyncClient(base_url=API_URL) as client:
        # Reset state if needed (e.g., drop DB or clear projections manually)

        # Place SELL order at 100
        sell_order = {
            "order_id": 1001,
            "side": "sell",
            "price": 100,
            "quantity": 10
        }
        res = await client.post("/orders", json=sell_order)
        assert res.status_code == 200

        # Place BUY order at 105 (should match)
        buy_order = {
            "order_id": 1002,
            "side": "buy",
            "price": 105,
            "quantity": 5
        }
        res = await client.post("/orders", json=buy_order)
        assert res.status_code == 200

        # Check trades
        res = await client.get("/trades")
        trades = res.json()
        assert len(trades) >= 1
        trade = trades[0]
        assert trade["price"] == 100
        assert trade["quantity"] == 5
        assert trade["buy_order_id"] == 1002
        assert trade["sell_order_id"] == 1001

        # Check order book: sell order should have 5 remaining
        res = await client.get("/orderbook")
        ob = res.json()
        assert "asks" in ob
        assert any(o["order_id"] == 1001 and o["quantity"] == 5 for o in ob["asks"])

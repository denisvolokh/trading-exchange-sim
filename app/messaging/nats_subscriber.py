import asyncio
from nats.aio.client import Client as NATS

NATS_URL = "nats://nats:4222"  # Use Docker service name, not localhost

async def handle_event(msg):
    subject = msg.subject
    data = msg.data.decode()
    print(f"[EVENT] {subject} → {data}")

async def run_nats_subscriber():
    client = NATS()
    await client.connect(servers=[NATS_URL])

    await client.subscribe("OrderPlaced.v1", cb=handle_event)
    await client.subscribe("OrderMatched.v1", cb=handle_event)
    await client.subscribe("OrderCancelled.v1", cb=handle_event)

    print("✅ Subscribed to order events. Waiting for messages...")

    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(run_nats_subscriber())

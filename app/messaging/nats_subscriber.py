import asyncio
import logging

from nats.aio.client import Client as NatsClient

NATS_URL = "nats://nats:4222"  # Use Docker service name, not localhost

logger = logging.getLogger(__name__)


async def handle_event(msg):
    subject = msg.subject
    data = msg.data.decode()

    logger.info(f"[+] Received message on subject '{subject}': {data}")


async def run_nats_subscriber():
    client = NatsClient()
    await client.connect(servers=[NATS_URL])
    logger.info("[+] Connected to NATS.")

    await client.subscribe("OrderPlaced.v1", cb=handle_event)
    await client.subscribe("OrderMatched.v1", cb=handle_event)
    await client.subscribe("OrderCancelled.v1", cb=handle_event)

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(run_nats_subscriber())

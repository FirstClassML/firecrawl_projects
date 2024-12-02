import aiohttp
from config import settings
import asyncio


async def send_price_alert(
    product_name: str, old_price: float, new_price: float, url: str
):
    drop_percentage = ((old_price - new_price) / old_price) * 100

    message = {
        "embeds": [
            {
                "title": "Price Drop Alert! 🔥",
                "description": f"**{product_name}**\nPrice dropped by {drop_percentage:.1f}%!\n"
                f"Old price: ${old_price:.2f}\n"
                f"New price: ${new_price:.2f}\n"
                f"[View Product]({url})",
                "color": 3066993,
            }
        ]
    }

    async with aiohttp.ClientSession() as session:
        await session.post(settings.DISCORD_WEBHOOK_URL, json=message)


async def test_webhook():
    await send_price_alert(
        product_name="Test Product",
        old_price=99.99,
        new_price=79.99,
        url="https://example.com",
    )


if __name__ == "__main__":
    asyncio.run(test_webhook())

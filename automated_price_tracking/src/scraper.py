from firecrawl import FirecrawlApp
from models import Product
from storage import Session, PriceHistory
from notifications import send_price_alert
from config import settings
import json
import asyncio
import warnings


async def check_single_product(url: str) -> Product:
    """Check a single product URL and return its details."""
    app = FirecrawlApp()

    data = app.scrape_url(
        url,
        params={
            "formats": ["extract"],
            "extract": {"schema": Product.model_json_schema()},
        },
    )

    return Product(**data["extract"])


async def check_prices():
    # Set up Firecrawl and database session
    app = FirecrawlApp()
    session = Session()

    # Open the file containing the product URLs to track
    with open(settings.PRODUCTS_FILE) as f:
        products_to_track = json.load(f)

    # Iterate over each product URL
    for product_url in products_to_track:

        try:
            product = await check_single_product(product_url)

            # Get the earliest, original price from the database for the given product URL
            last_price = (
                session.query(PriceHistory)
                .filter_by(product_url=product_url)
                .order_by(PriceHistory.timestamp.asc())
                .first()
            )

            if last_price and last_price.price > product.price:
                drop_pct = last_price.price - product.price

                # Send a Discord notification if the price drop is greater than the threshold
                if drop_pct >= settings.PRICE_DROP_THRESHOLD:
                    await send_price_alert(
                        product.name, last_price.price, product.price, product_url
                    )

            # Save new price
            session.add(
                PriceHistory(
                    product_url=product_url,
                    price=product.price,
                    product_name=product.name,
                )
            )
        except Exception as e:
            warnings.warn(f"Error checking product {product_url}: {e}")
            continue

    session.commit()


if __name__ == "__main__":

    asyncio.run(check_prices())

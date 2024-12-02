from firecrawl import FirecrawlApp
from models import Product
from storage import Session, PriceHistory
from notifications import send_price_alert
from config import settings
import json
import asyncio
import warnings


async def check_prices():
    # Set up Firecrawl and database session
    app = FirecrawlApp()
    session = Session()

    # Open the file containing the product URLs to track
    with open(settings.PRODUCTS_FILE) as f:
        products_to_track = json.load(f)

    # Iterate over each product URL
    for product_url in products_to_track:

        # Extract with Firecrawl based on the Product schema in models.py
        data = app.scrape_url(
            product_url,
            params={
                "formats": ["extract"],
                "extract": {"schema": Product.model_json_schema()},
            },
        )

        product = Product(**data["extract"])

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
                product_url=product_url, price=product.price, product_name=product.name
            )
        )

    session.commit()


if __name__ == "__main__":

    asyncio.run(check_prices())

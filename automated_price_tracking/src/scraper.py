from firecrawl import FirecrawlApp
from models import Product
from storage import Session, PriceHistory
from notifications import send_price_alert
from config import settings
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

    try:
        # Get all products from database
        products = session.query(Product).all()

        # Iterate over each product
        for product in products:
            try:
                updated_product = await check_single_product(product.url)

                # Get the earliest price from the database
                last_price = (
                    session.query(PriceHistory)
                    .filter_by(product_url=product.url)
                    .order_by(PriceHistory.timestamp.asc())
                    .first()
                )

                if last_price and last_price.price > updated_product.price:
                    drop_pct = (
                        last_price.price - updated_product.price
                    ) / last_price.price

                    # Send notification if price drop exceeds threshold
                    if drop_pct >= settings.PRICE_DROP_THRESHOLD:
                        await send_price_alert(
                            product.name,
                            last_price.price,
                            updated_product.price,
                            product.url,
                        )

                # Save new price
                session.add(
                    PriceHistory(
                        product_url=product.url,
                        price=updated_product.price,
                        product_name=product.name,
                    )
                )
            except Exception as e:
                warnings.warn(f"Error checking product {product.url}: {e}")
                continue

        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    asyncio.run(check_prices())

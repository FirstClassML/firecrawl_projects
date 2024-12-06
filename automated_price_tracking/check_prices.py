import os
from database import Database
from dotenv import load_dotenv
from firecrawl import FirecrawlApp
from scraper import scrape_product

load_dotenv()

db = Database(os.getenv("POSTGRES_URL"))
app = FirecrawlApp()


def check_prices():
    products = db.get_all_products()
    product_urls = set(product.url for product in products)

    for product_url in product_urls:
        # Retrieve updated product data
        updated_product = scrape_product(product_url)

        # Add the price to the database
        db.add_price(updated_product)
        print(f"Added new price entry for {updated_product['name']}")


if __name__ == "__main__":
    check_prices()

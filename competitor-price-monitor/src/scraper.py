import warnings

warnings.filterwarnings("ignore")

from datetime import datetime
from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()
app = FirecrawlApp()


class CompetitorProduct(BaseModel):
    """Schema for extracting competitor product data"""

    name: str = Field(description="The name/title of the product")
    price: float = Field(description="The current price of the product")
    image_url: str | None = Field(None, description="URL of the main product image")


def scrape_competitor_product(url: str) -> dict:
    """
    Scrape product information from a competitor's webpage
    """
    extracted_data = app.scrape_url(
        url,
        params={
            "formats": ["extract"],
            "extract": {
                "schema": CompetitorProduct.model_json_schema(),
            },
        },
    )

    # Add timestamp to the extracted data
    data = extracted_data["extract"]
    data["last_checked"] = datetime.utcnow()

    return data


if __name__ == "__main__":
    print(
        scrape_competitor_product(
            "https://www.bestbuy.com/site/samsung-85-class-du7200-series-crystal-uhd-4k-smart-tizen-tv-2024/6575123.p?skuId=6575123"
        )
    )

import json
import boto3

from firecrawl import FirecrawlApp
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from datetime import datetime

load_dotenv()


class Product(BaseModel):
    name: str = Field(description="The name of the product")
    description: str = Field(description="A short description of the product")
    url: str = Field(description="The URL of the product")
    topics: list[str] = Field(
        description="A list of topics the product belongs to. Can be found below the product description."
    )
    n_upvotes: int = Field(description="The number of upvotes the product has")
    n_comments: int = Field(description="The number of comments the product has")
    rank: int = Field(
        description="The rank of the product on Product Hunt's Yesterday's Top Products section."
    )
    logo_url: str = Field(description="The URL of the product's logo.")


class YesterdayTopProducts(BaseModel):
    products: list[Product] = Field(
        description="A list of top products from yesterday on Product Hunt."
    )


BASE_URL = "https://www.producthunt.com"


def get_yesterday_top_products():
    app = FirecrawlApp()

    data = app.scrape_url(
        BASE_URL,
        params={
            "formats": ["extract"],
            "extract": {
                "schema": YesterdayTopProducts.model_json_schema(),
                "prompt": "Extract the top products listed under the 'Yesterday's Top Products' section. There will be exactly 5 products.",
            },
        },
    )

    return data["extract"]["products"]


def save_yesterday_top_products():
    products = get_yesterday_top_products()

    # Initialize S3 client
    s3 = boto3.client("s3")

    # Create filename with date
    date_str = datetime.now().strftime("%Y_%m_%d")
    filename = f"ph_top_products_{date_str}.json"

    # Upload to S3
    s3.put_object(Bucket="sample-bucket-1801", Key=filename, Body=json.dumps(products))


if __name__ == "__main__":
    save_yesterday_top_products()

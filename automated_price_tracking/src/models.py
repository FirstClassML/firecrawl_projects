from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class Product(BaseModel):
    url: str = Field(description="The URL of the product")
    name: str = Field(description="The product name/title")
    price: float = Field(description="The current price of the product")
    currency: str = Field(description="Currency code (USD, EUR, etc)")
    check_date: str = Field(
        default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%d")
    )
    main_image_url: str = Field(description="The URL of the main image of the product")

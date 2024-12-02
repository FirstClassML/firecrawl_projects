import asyncio
import streamlit as st
import json
from datetime import datetime
import pandas as pd
from sqlalchemy import desc
from urllib.parse import urlparse
import plotly.express as px

from models import Product as PydanticProduct
from storage import Session, PriceHistory, Product
from config import settings
from scraper import check_single_product


class ProductManager:
    def __init__(self):
        self.session = Session()

    def load_products(self):
        try:
            db_products = self.session.query(Product).all()
            return [
                PydanticProduct(
                    url=p.url,
                    name=p.name,
                    price=p.price,
                    currency=p.currency,
                    check_date=p.check_date,
                    main_image_url=p.main_image_url,
                )
                for p in db_products
            ]
        except Exception:
            return []

    def save_product(self, pydantic_product):
        db_product = Product(
            url=pydantic_product.url,
            name=pydantic_product.name,
            price=pydantic_product.price,
            currency=pydantic_product.currency,
            check_date=pydantic_product.check_date,
            main_image_url=pydantic_product.main_image_url,
        )
        self.session.add(db_product)
        self.session.commit()

    def remove_product(self, url):
        product = self.session.query(Product).filter_by(url=url).first()
        if product:
            self.session.query(PriceHistory).filter_by(product_url=url).delete()
            self.session.delete(product)
            self.session.commit()


class PriceTracker:
    def __init__(self):
        self.session = Session()
        self.product_manager = ProductManager()

    def __del__(self):
        self.session.close()

    async def add_product(self, url):
        if not self._validate_url(url):
            return False, "Please enter a valid URL"

        try:
            # Normalize Amazon URL by extracting the product ID
            normalized_url = self._normalize_amazon_url(url)
            if not normalized_url:
                return False, "Invalid Amazon product URL"

            # Check if product exists using normalized URL
            existing_product = (
                self.session.query(Product).filter_by(url=normalized_url).first()
            )
            if existing_product:
                return False, "Product already being tracked!"

            # Scrape product using original URL
            product = await check_single_product(url)

            # Use normalized URL for database
            db_product = Product(
                url=normalized_url,  # Use normalized URL
                name=product.name,
                price=product.price,
                currency=product.currency,
                check_date=product.check_date,
                main_image_url=product.main_image_url,
            )

            self.session.add(db_product)
            self.session.commit()

            # Use normalized URL for price history
            self._create_price_history(normalized_url, product.price)

            return (
                True,
                f"Added and checked initial price for: {product.name} - ${product.price:.2f}",
            )

        except Exception as e:
            self.session.rollback()
            return False, f"Error scraping product: {str(e)}"

    def _validate_url(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def _create_price_history(self, url, price):
        entry = PriceHistory(product_url=url, price=price, timestamp=datetime.now())
        self.session.add(entry)
        self.session.commit()

    def _normalize_amazon_url(self, url):
        """Normalize Amazon URL to a consistent format."""
        try:
            # Extract product ID (ASIN) from URL
            if "/dp/" in url:
                asin = url.split("/dp/")[1].split("/")[0]
            elif "/gp/product/" in url:
                asin = url.split("/gp/product/")[1].split("/")[0]
            elif "/gp/aw/d/" in url:
                asin = url.split("/gp/aw/d/")[1].split("/")[0]
            else:
                return None

            # Return normalized URL format
            return f"https://www.amazon.com/dp/{asin}"
        except Exception:
            return None


class DashboardUI:
    def __init__(self):
        self.tracker = PriceTracker()

    def render_sidebar(self):
        st.sidebar.header("Add New Product")
        new_url = st.sidebar.text_input("Product URL")

        if st.sidebar.button("Add Product") and new_url:
            success, message = asyncio.run(self.tracker.add_product(new_url))
            if success:
                st.sidebar.success(message)
                st.rerun()
            else:
                st.sidebar.error(message)

    def create_price_chart(self, price_history):
        fig = px.line(price_history, x="timestamp", y="price", title=None)
        fig.update_layout(
            xaxis_title=None,
            yaxis_title="Price ($)",
            showlegend=False,
            margin=dict(l=0, r=0, t=0, b=0),
            height=300,
        )
        fig.update_xaxes(tickformat="%Y-%m-%d %H:%M", tickangle=45)
        fig.update_yaxes(tickprefix="$", tickformat=".2f")
        return fig

    def render_product_section(self, product):
        latest_price = (
            self.tracker.session.query(PriceHistory)
            .filter_by(product_url=product.url)
            .order_by(desc(PriceHistory.timestamp))
            .first()
        )

        with st.expander(f"{product.name}", expanded=False):
            col1, col2, col3 = st.columns([3, 1, 1])
            price_history = pd.read_sql(
                self.tracker.session.query(PriceHistory)
                .filter_by(product_url=product.url)
                .statement,
                self.tracker.session.bind,
            )

            if not price_history.empty:
                fig = self.create_price_chart(price_history)
                col1.plotly_chart(fig, use_container_width=True)
                col2.metric("Current Price", f"${latest_price.price:.2f}", delta=None)
            else:
                col1.info("No price history available")

            # Add visit product button
            col3.link_button("Visit Product", product.url)

            if st.button("Remove from tracking", key=f"remove_{product.url}"):
                self._remove_product(product.url)

    def _remove_product(self, url):
        self.tracker.product_manager.remove_product(url)
        st.success("Product removed from tracking!")
        st.rerun()

    def render(self):
        st.title("Price Tracker Dashboard")
        self.render_sidebar()
        st.header("Tracked Products")

        products = self.tracker.product_manager.load_products()
        if not products:
            st.info("No products are being tracked. Add some using the sidebar!")
        else:
            for product in products:
                self.render_product_section(product)


def main():
    dashboard = DashboardUI()
    dashboard.render()


if __name__ == "__main__":
    main()

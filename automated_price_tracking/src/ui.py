import asyncio
import streamlit as st
import json
from datetime import datetime
import pandas as pd
from sqlalchemy import desc
from urllib.parse import urlparse
import plotly.express as px

from models import Product
from storage import Session, PriceHistory
from config import settings
from scraper import check_single_product


def load_products():
    try:
        with open(settings.PRODUCTS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_products(products):
    with open(settings.PRODUCTS_FILE, "w") as f:
        json.dump(products, f, indent=2)


def main():
    st.title("Price Tracker Dashboard")

    # Sidebar for adding new products
    st.sidebar.header("Add New Product")
    new_url = st.sidebar.text_input("Product URL")

    if st.sidebar.button("Add Product"):
        if new_url:
            # Validate URL
            try:
                result = urlparse(new_url)
                if all([result.scheme, result.netloc]):
                    # Check if product can be scraped
                    try:
                        product = asyncio.run(check_single_product(new_url))
                        products = load_products()
                        if new_url not in products:
                            products.append(new_url)
                            save_products(products)
                            st.sidebar.success(f"Added: {product.name}")
                        else:
                            st.sidebar.warning("Product already being tracked!")
                    except Exception as e:
                        st.sidebar.error(f"Error scraping product: {str(e)}")
                else:
                    st.sidebar.error("Please enter a valid URL")
            except ValueError:
                st.sidebar.error("Please enter a valid URL")

    # Main content - Product List
    st.header("Tracked Products")

    session = Session()
    products = load_products()

    if not products:
        st.info("No products are being tracked. Add some using the sidebar!")
    else:
        for url in products:
            # Get latest price data
            latest_price = (
                session.query(PriceHistory)
                .filter_by(product_url=url)
                .order_by(desc(PriceHistory.timestamp))
                .first()
            )

            # Create expander for each product
            with st.expander(f"Product: {url}", expanded=True):
                col1, col2 = st.columns([3, 1])

                # Price history chart
                price_history = pd.read_sql(
                    session.query(PriceHistory).filter_by(product_url=url).statement,
                    session.bind,
                )

                if not price_history.empty:
                    # Create plotly figure
                    fig = px.line(
                        price_history,
                        x="timestamp",
                        y="price",
                        title=None,
                    )

                    # Customize the layout
                    fig.update_layout(
                        xaxis_title=None,
                        yaxis_title="Price ($)",
                        showlegend=False,
                        margin=dict(l=0, r=0, t=0, b=0),
                        height=300,
                    )

                    # Format x-axis to show readable dates
                    fig.update_xaxes(
                        tickformat="%Y-%m-%d %H:%M",
                        tickangle=45,
                    )

                    # Format y-axis to show dollar amounts
                    fig.update_yaxes(
                        tickprefix="$",
                        tickformat=".2f",
                    )

                    # Display the plot
                    col1.plotly_chart(fig, use_container_width=True)

                    # Latest price info
                    col2.metric(
                        "Current Price",
                        f"${latest_price.price:.2f}",
                        delta=None,
                    )
                else:
                    col1.info("No price history yet")
                    if col1.button("Check price now", key=f"check_{url}"):
                        try:
                            product = asyncio.run(check_single_product(url))

                            # Create new price history entry
                            new_price_entry = PriceHistory(
                                product_url=url,
                                price=product.price,
                                timestamp=datetime.now(),
                            )
                            session.add(new_price_entry)
                            session.commit()

                            st.success(
                                f"Price checked for: {product.name} - ${product.price:.2f}"
                            )
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error checking price: {str(e)}")
                            session.rollback()

                # Remove product button
                if st.button("Remove from tracking", key=f"remove_{url}"):
                    products.remove(url)
                    save_products(products)
                    st.success("Product removed from tracking!")
                    st.rerun()

    session.close()


if __name__ == "__main__":
    main()

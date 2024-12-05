import os
import streamlit as st

from utils import is_valid_url
from database import Database
from dotenv import load_dotenv
from scraper import scrape_product

load_dotenv()

with st.spinner("Loading database..."):
    db = Database(os.getenv("POSTGRES_URL"))


# Set up sidebar
with st.sidebar:
    st.title("Add New Product")
    product_url = st.text_input("Product URL")
    add_button = st.button("Add Product")

    if add_button:
        if not product_url:
            st.error("Please enter a product URL")
        elif not is_valid_url(product_url):
            st.error("Please enter a valid URL")
        else:
            db.add_product(product_url)
            with st.spinner("Added product to database. Scraping product data..."):
                product_data = scrape_product(product_url)
                db.add_price(product_data)
            st.success("Product is now being tracked!")

# Main content
st.title("Price Tracker Dashboard")
st.markdown("## Tracked Products")

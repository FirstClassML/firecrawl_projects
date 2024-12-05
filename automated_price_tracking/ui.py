import streamlit as st

# Set up sidebar
with st.sidebar:
    st.title("Add New Product")
    product_url = st.text_input("Product URL")
    add_button = st.button("Add Product")

# Main content
st.title("Price Tracker Dashboard")
st.markdown("## Tracked Products")

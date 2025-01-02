import os
import time
import webbrowser

from dotenv import load_dotenv
from scraper import scrape_competitor_product
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import urlparse
import streamlit as st
from database import Base, Competitor, Product

# Load environment variables
load_dotenv()

# Database setup
engine = create_engine(os.getenv("POSTGRES_URL"))
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def add_product():
    """Form to add a new product"""
    with st.form("add_product"):
        name = st.text_input("Product Name")
        price = st.number_input("Your Price", min_value=0.0, step=0.01)
        url = st.text_input("Product URL (optional)")

        if st.form_submit_button("Add Product"):
            session = Session()
            product = Product(name=name, your_price=price, url=url)
            session.add(product)
            session.commit()
            session.close()
            st.success(f"Added product: {name}")
            return True
    return False


def display_competitor_metrics(product, comp):
    """Display competitor price comparison metrics"""
    st.markdown(f"#### {urlparse(comp.url).netloc}")
    cols = st.columns([1, 2, 1, 1])

    diff = ((comp.current_price - product.your_price) / product.your_price) * 100

    with cols[0]:
        st.metric(
            label="💰 Competitor price",
            value=f"${comp.current_price:.2f}",
            delta=f"{diff:+.1f}%",
            delta_color="normal",
        )
    with cols[1]:
        st.markdown(f"**🕒 Checked:** {comp.last_checked.strftime('%Y-%m-%d %H:%M')}")
    with cols[2]:
        st.button(
            "Visit product",
            key=f"visit_btn_{comp.id}",
            use_container_width=True,
            on_click=lambda: webbrowser.open_new_tab(comp.url),
        )
    with cols[3]:
        st.button(
            "🗑️",
            key=f"delete_comp_btn_{comp.id}",
            type="primary",
            use_container_width=True,
            on_click=lambda: delete_competitor(comp.id),
        )


def display_product_details(product):
    """Display details for a single product"""
    st.subheader(product.name)
    cols = st.columns([1, 2])
    with cols[0]:
        st.metric(
            label="Your Price",
            value=f"${product.your_price:.2f}",
        )
    with cols[1]:
        col1, col2 = st.columns(2)
        with col1:
            if product.url:
                st.button(
                    "Visit product",
                    key=f"visit_btn_{product.id}",
                    use_container_width=True,
                    on_click=lambda: webbrowser.open_new_tab(product.url),
                )
            else:
                st.text("No URL provided")
        with col2:
            st.button(
                "🗑️ Delete",
                key=f"delete_btn_{product.id}",
                type="primary",
                use_container_width=True,
                on_click=lambda: delete_product(product.id),
            )


def display_competitors(product):
    """Display all competitors for a product"""
    if product.competitors:
        with st.expander("View competitors", expanded=False):
            for comp in product.competitors:
                display_competitor_metrics(product, comp)
    else:
        st.info("No competitors added yet")


def add_competitor_form(product, session):
    """Form to add a new competitor"""
    with st.expander("Add new competitor", expanded=False):
        with st.form(f"add_competitor_{product.id}"):
            competitor_url = st.text_input("🔗 Competitor product URL")
            col1, col2 = st.columns([3, 1])
            with col2:
                submit = st.form_submit_button(
                    "Add competitor", use_container_width=True
                )

            if submit:
                try:
                    with st.spinner("Fetching competitor data..."):
                        data = scrape_competitor_product(competitor_url)
                        competitor = Competitor(
                            product_id=product.id,
                            url=competitor_url,
                            name=data["name"],
                            current_price=data["price"],
                            image_url=data.get("image_url"),
                            last_checked=data["last_checked"],
                        )
                        session.add(competitor)
                        session.commit()
                        st.success("✅ Competitor added successfully!")

                        # Refresh the page
                        time.sleep(1)
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Error adding competitor: {str(e)}")


def delete_product(product_id: str):
    """Delete a product and all its competitors"""
    session = Session()
    product = session.query(Product).filter_by(id=product_id).first()
    if product:
        session.delete(product)
        session.commit()
    session.close()


def delete_competitor(competitor_id: str):
    """Delete a competitor"""
    session = Session()
    competitor = session.query(Competitor).filter_by(id=competitor_id).first()
    if competitor:
        session.delete(competitor)
        session.commit()
    session.close()


def main():
    st.title("Competitor Price Monitor")
    st.markdown(
        "##### Compare your product prices to competitors' prices. Input your product details and competitors' URLs to get started."
    )
    st.markdown("### Tracked Products")
    st.markdown("---")

    # Sidebar for adding new products
    with st.sidebar:
        st.header("Add New Product")
        add_product()

    # Main content area
    session = Session()
    products = session.query(Product).all()

    if not products:
        st.info("No products added yet. Use the sidebar to add your first product.")
    else:
        for product in products:
            with st.container():
                display_product_details(product)
                display_competitors(product)
                add_competitor_form(product, session)

    session.close()


if __name__ == "__main__":
    main()

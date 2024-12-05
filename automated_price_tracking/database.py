from sqlalchemy import create_engine, Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class Product(Base):
    __tablename__ = "products"

    url = Column(String, primary_key=True)
    prices = relationship(
        "PriceHistory", back_populates="product", cascade="all, delete-orphan"
    )


class PriceHistory(Base):
    __tablename__ = "price_histories"

    id = Column(String, primary_key=True)
    product_url = Column(String, ForeignKey("products.url"))
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    main_image_url = Column(String)
    timestamp = Column(DateTime, nullable=False)
    product = relationship("Product", back_populates="prices")


class Database:
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_product(self, url):
        session = self.Session()
        try:
            # Create the product entry
            product = Product(url=url)
            session.merge(product)  # merge will update if exists, insert if not
            session.commit()
        finally:
            session.close()

    def product_exists(self, url):
        session = self.Session()
        try:
            return session.query(Product).filter(Product.url == url).first() is not None
        finally:
            session.close()

    # def add_price(self, url, price, timestamp):
    #     """Add a price entry for a product"""
    #     session = self.Session()
    #     try:
    #         price_history = PriceHistory(
    #             id=f"{url}_{timestamp.strftime('%Y%m%d%H%M%S')}",
    #             product_url=url,
    #             price=price,
    #             timestamp=timestamp,
    #         )
    #         session.add(price_history)
    #         session.commit()
    #     finally:
    #         session.close()

    # def get_price_history(self, url):
    #     """Get price history for a product"""
    #     session = self.Session()
    #     try:
    #         return (
    #             session.query(PriceHistory)
    #             .filter(PriceHistory.product_url == url)
    #             .order_by(PriceHistory.timestamp.desc())
    #             .all()
    #         )
    #     finally:
    #         session.close()

    # def remove_product(self, url):
    #     """Remove a product and its price history"""
    #     session = self.Session()
    #     try:
    #         product = session.query(Product).filter(Product.url == url).first()
    #         if product:
    #             session.delete(
    #                 product
    #             )  # This will also delete associated price history due to cascade
    #             session.commit()
    #     finally:
    #         session.close()
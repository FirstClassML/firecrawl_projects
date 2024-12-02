from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

Base = declarative_base()


class Product(Base):
    __tablename__ = "products"

    url = Column(String, primary_key=True)
    name = Column(String)
    price = Column(Float)
    currency = Column(String)
    check_date = Column(String)
    main_image_url = Column(String)


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True)
    product_url = Column(String, index=True)
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)


engine = create_engine("sqlite:///data/price_history.db")
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


def change_product_price(product_url: str, new_price: float):
    session = Session()
    session.query(PriceHistory).filter(PriceHistory.product_url == product_url).update(
        {"price": new_price}
    )

    session.commit()


def print_price_history():
    session = Session()
    records = session.query(PriceHistory).all()

    for record in records:
        print(f"Product: {record.product_name}")
        print(f"Price: ${record.price:.2f}")
        print(f"Timestamp: {record.timestamp}")
        print("-" * 80)


if __name__ == "__main__":
    # change_product_price(
    #     "https://www.amazon.com/gp/product/1718501900",
    #     1000.99,
    # )

    print_price_history()

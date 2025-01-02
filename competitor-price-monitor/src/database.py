from sqlalchemy import create_engine, Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    your_price = Column(Float, nullable=False)
    url = Column(String)
    competitors = relationship(
        "Competitor", back_populates="product", cascade="all, delete-orphan"
    )


class Competitor(Base):
    __tablename__ = "competitors"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String, ForeignKey("products.id"))
    url = Column(String, nullable=False)
    name = Column(String)
    current_price = Column(Float)
    last_checked = Column(DateTime, default=datetime.utcnow)
    image_url = Column(String)
    product = relationship("Product", back_populates="competitors")


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    engine = create_engine(os.getenv("POSTGRES_URL"))
    Base.metadata.create_all(engine)

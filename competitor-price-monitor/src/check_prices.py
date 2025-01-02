import os
from database import Base, Product, Competitor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from scraper import scrape_competitor_product
from dotenv import load_dotenv

load_dotenv()

# Database setup
engine = create_engine(os.getenv("POSTGRES_URL"))
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def update_competitor_prices():
    """Update all competitor prices"""
    session = Session()
    competitors = session.query(Competitor).all()

    for competitor in competitors:
        try:
            # Scrape updated data
            data = scrape_competitor_product(competitor.url)

            # Update competitor
            competitor.current_price = data["price"]
            competitor.last_checked = data["last_checked"]

            print(f"Updated price for {competitor.name}: ${data['price']}")
        except Exception as e:
            print(f"Error updating {competitor.name}: {str(e)}")

    session.commit()
    session.close()


if __name__ == "__main__":
    update_competitor_prices()

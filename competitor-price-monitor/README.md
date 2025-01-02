# Competitor Price Monitor

A simple price monitoring system to compare your product prices against competitors in real-time.

## Features

- **Product Management**
  - Add your products with their current prices
  - Track multiple competitors for each product
  - Support for various e-commerce platforms through Firecrawl API

- **Price Comparison**
  - Clean, straightforward comparison dashboard
  - Visual price difference indicators
  - Automated price checking every 6 hours

- **Notifications**
  - Discord alerts when competitor prices change
  - Customizable price change threshold for notifications

## How It Works

1. **Add Your Product**
   - Enter product name and your price
   - Add product URL (optional)

2. **Add Competitors**
   - For each product, add competitor webpage URLs containing the same product you are tracking
   - System automatically extracts:
     - Competitor product name
     - Current price

3. **Monitor & Compare**
   - Dashboard shows your price vs competitor prices
   - Clear visual indicators showing if you're priced higher or lower
   - Percentage difference from your price

## Setup

1. Clone the repository
2. Install dependencies:

   ```bash
   poetry install
   ```

3. Configure environment variables:

   ```bash
   cp .env.example .env
   ```

   Add your:
   - Firecrawl API key
   - PostgreSQL database credentials
   - Discord webhook URL (optional)

4. Start the Streamlit app:

   ```bash
   streamlit run app.py
   ```

## Database Schema

- **Products**
  - id (UUID)
  - name
  - your_price
  - url (optional)

- **Competitors**
  - id (UUID)
  - product_id (FK)
  - url
  - name
  - current_price
  - last_checked
  - image_url

## Tech Stack

- Python 3.9+
- Streamlit for UI
- Firecrawl for web scraping
- PostgreSQL for data storage
- SQLAlchemy for ORM

## License

MIT

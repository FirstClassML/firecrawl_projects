# Sales Lead Extractor

A Streamlit web application that extracts structured data from website URLs using AI-powered web scraping. Perfect for sales teams and marketers who need to gather lead information from company websites efficiently.

## Features

- 🌐 Batch URL Processing: Upload multiple URLs via CSV or TXT files
- 🎯 Dynamic Field Extraction: Define custom fields you want to extract
- 🤖 AI-Powered Scraping: Uses Firecrawl API for intelligent data extraction
- 📊 Excel Export: Results are automatically exported to Excel files
- 🚀 User-Friendly Interface: Built with Streamlit for easy interaction

## Installation

1. Clone the repository:

```bash
git clone <https://github.com/yourusername/sales-lead-extractor.git>
cd sales-lead-extractor
```

2. Install Poetry (if not already installed):

```bash
curl -sSL <https://install.python-poetry.org> | python3 -
```

3. Install dependencies:

```bash
poetry install
```

4. Create a `.env` file in the root directory and add your Firecrawl API key:

```plaintext
FIRECRAWL_API_KEY=your_api_key_here
```

## Usage

1. Start the Streamlit app:

```bash
poetry run streamlit run src/app.py
```

2. Open your browser and navigate to `http://localhost:8501`
3. Upload a file containing URLs (CSV or TXT format)
4. Define the fields you want to extract (e.g., company_name, email, phone)
5. Click "Start Extraction" and wait for the results
6. Download the Excel file with the extracted data

## Input File Format

- CSV Example

```csv
https://www.company1.com
https://www.company2.com
https://www.company3.com
```

### TXT Example

```text
https://www.company1.com
https://www.company2.com
https://www.company3.com
```

## Dependencies

- Python 3.10+
- Streamlit
- Firecrawl Python SDK
- Pandas
- Pydantic
- Python-dotenv
- OpenPyXL

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature/improvement`)
6. Create a Pull Request

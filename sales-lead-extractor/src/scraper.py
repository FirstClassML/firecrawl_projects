from firecrawl import FirecrawlApp
from typing import Dict, List
from datetime import datetime
import pandas as pd
from models import DynamicLeadModel


class LeadScraper:
    def __init__(self):
        self.app = FirecrawlApp()

    async def scrape_leads(self, urls: List[str], fields: Dict[str, str]) -> str:
        """Scrape multiple leads using Firecrawl's batch extraction endpoint"""
        # Create dynamic model
        model = DynamicLeadModel.create_model(fields)

        # Extract data for all URLs at once
        data = self.app.batch_scrape_urls(
            urls,
            params={
                "formats": ["extract"],
                "extract": {"schema": model.model_json_schema()},
            },
        )

        # Process results
        results = [
            {"url": result["metadata"]["url"], **result["extract"]}
            for result in data["data"]
        ]

        # Convert to DataFrame
        df = pd.DataFrame(results)

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/leads_{timestamp}.xlsx"
        df.to_excel(filename, index=False)

        return filename

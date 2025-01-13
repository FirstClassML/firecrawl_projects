import asyncio
from dotenv import load_dotenv
from typing import Dict, List
import os
import pandas as pd
from scraper import LeadScraper
import streamlit as st
import time

load_dotenv()


def load_urls(uploaded_file) -> List[str]:
    """Load URLs from uploaded file"""
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file, header=None)
        return df.iloc[:, 0].tolist()
    else:
        content = uploaded_file.getvalue().decode()
        return [url.strip() for url in content.split("\n") if url.strip()]


def main():
    st.title("Sales Lead Extractor")
    st.write(
        "Upload a file with website URLs of your leads and define the fields to extract"
    )

    # Sample input and output

    # File upload
    uploaded_file = st.file_uploader("Choose a file", type=["csv", "txt"])

    if uploaded_file:
        urls = load_urls(uploaded_file)
        st.write(f"Loaded {len(urls)} URLs")

        # Dynamic field input
        st.subheader("Define Fields to Extract")

        fields: Dict[str, str] = {}
        col1, col2 = st.columns(2)

        with col1:
            num_fields = st.number_input(
                "Number of fields", min_value=1, max_value=10, value=3
            )

        for i in range(num_fields):
            col1, col2 = st.columns(2)
            with col1:
                field_name = st.text_input(f"Field {i+1} name", key=f"name_{i}")

                # Convert field_name to lower snake case
                field_name = field_name.lower().replace(" ", "_")

            with col2:
                field_desc = st.text_input(f"Field {i+1} description", key=f"desc_{i}")

            if field_name and field_desc:
                fields[field_name] = field_desc

        if st.button("Start Extraction") and fields:
            with st.spinner(
                "Extracting data. This may take a while, so don't close the window."
            ):
                start_time = time.time()
                scraper = LeadScraper()

                # Run scraping asynchronously
                result_file = asyncio.run(scraper.scrape_leads(urls, fields))

                elapsed_time = time.time() - start_time
                elapsed_mins = int(elapsed_time // 60)
                elapsed_secs = int(elapsed_time % 60)

                # Show download link
                with open(result_file, "rb") as f:
                    st.download_button(
                        "Download Results",
                        f,
                        file_name=os.path.basename(result_file),
                        mime="text/csv",
                    )
                st.balloons()
                st.success(
                    f"Extraction complete! Time taken: {elapsed_mins}m {elapsed_secs}s"
                )


if __name__ == "__main__":
    main()

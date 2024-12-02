# Automated Price Tracking Tool Using Firecrawl

I want to build an automated price tracking tool using Firecrawl. Here are the features the app must have:

1. Must be run on a schedule I specify with GitHub actions
2. Must run for any webpage I throw at it (Firecrawl handles this using its schema and AI-based extraction)
3. Must be able to handle multiple products at once
4. Keep price history for each tracked item
5. It must send alerts to Discord
6. Configure the price drop threshold like 5, 10, 15%, etc.
7. Save app price history to a database
8. A streamlit UI for this project so that users can add or remove products from tracking using a simple URL input.
9. The project must be deployable to Streamlit Cloud

Here is a typical workflow users must experience when they visit the app:

They open the app and the app immediately presents them with the existing products in the database and their price history chart. If there are no products, it should inform the user as such and gently nudge them to enter a product through the sidebar.

In the sidebar, there must always be an input field for a product URL. When the URL is entered, it must first be checked against existing products. If not, then, its page must scraped, its initial price extracted and saved and it must be added to the list of tracked products and added to the UI. 

There must be a button to remove existing products and also a button for visiting the products page. 

# Automated Price Tracking Tool Using Firecrawl

I want to build an automated price tracking tool using Firecrawl. Here are the features the app must have:

1. Must be run on a schedule I specify with GitHub actions
2. Must run for any webpage I throw at it (Firecrawl handles this using its schema and AI-based extraction)
3. Must be able to handle multiple products at once
4. Keep price history for each tracked item
5. It must send alerts to Discord or Slack or as SMS (whichever is easiest) when an item price drops
6. Configure the price drop threshold like 5, 10, 15%, etc.
7. Save app price history to somewhere (suggest best options in terms of usability).
8. A streamlit UI for this project so that users can add or remove products from tracking using a simple URL input.
9. The project must be deployable to Streamlit Cloud

Give me a step-by-step plan to build this product in Python and Firecrawl. The plan must conform to software engineering best practices.

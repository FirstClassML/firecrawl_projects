from fastapi import FastAPI, Request  # type: ignore
from firecrawl import FirecrawlApp
import uvicorn  # type: ignore
import threading
import time
from datetime import datetime
from dotenv import load_dotenv
import logging
import requests
import asyncio
import nest_asyncio

load_dotenv()
nest_asyncio.apply()  # Enable nested event loops

# Initialize FastAPI for webhook server
app = FastAPI()

# Configure uvicorn logging to be less verbose
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").setLevel(logging.ERROR)


def get_timestamp():
    """Return current timestamp in readable format"""
    return datetime.now().strftime("%H:%M:%S")


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    event_type = data.get("type")
    crawl_id = data.get("id")
    timestamp = get_timestamp()

    # Print progress based on event type with timestamps
    if event_type == "crawl.started":
        print(f"[{timestamp}] 🚀 Crawl started: {crawl_id}")
    elif event_type == "crawl.page":
        pages = data.get("data", [])
        if pages:
            url = pages[0].get("metadata", {}).get("url", "Unknown URL")
            print(f"[{timestamp}] 📄 Crawled: {url}")
    elif event_type == "crawl.completed":
        print(f"[{timestamp}] ✅ Crawl completed: {crawl_id}")
    elif event_type == "crawl.failed":
        print(f"[{timestamp}] ❌ Crawl failed: {data.get('error')}")

    return {"status": "success"}


def start_webhook_server():
    """Start the webhook server in the background"""
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")


def wait_for_webhook_server():
    """Wait for webhook server to be ready"""
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get("http://127.0.0.1:8000")
            return True
        except requests.exceptions.ConnectionError:
            if i < max_retries - 1:
                time.sleep(0.5)
    return False


async def monitor_crawl():
    """Monitor crawl progress using async approach"""
    # Initialize Firecrawl
    firecrawl = FirecrawlApp()

    # Start crawl with webhook
    result = await firecrawl.async_crawl_url(
        url="https://docs.stripe.com/",
        params={
            "webhook": "http://127.0.0.1:8000/webhook",
            "maxDepth": 3,
            "scrapeOptions": {"formats": ["markdown"]},
        },
    )

    crawl_id = result.get("id")
    print(f"Crawl started with ID: {crawl_id}")

    while True:
        try:
            status = await firecrawl.async_check_crawl_status(crawl_id)
            if status.get("status") == "completed":
                print(f"\n[{get_timestamp()}] Crawl completed!")
                break
            elif status.get("status") == "failed":
                print(f"\n[{get_timestamp()}] Crawl failed: {status.get('error')}")
                break

            await asyncio.sleep(1)
        except KeyboardInterrupt:
            print(f"\n[{get_timestamp()}] Monitor stopped")
            break


def main():
    print("\nStarting webhook server...")

    # Start webhook server in background thread
    webhook_thread = threading.Thread(target=start_webhook_server, daemon=True)
    webhook_thread.start()

    # Wait for webhook server to be ready
    if not wait_for_webhook_server():
        print("Failed to start webhook server")
        return

    print("Webhook server is ready")
    print("Starting crawl... (Press Ctrl+C to stop)\n")

    try:
        # Run the async monitor
        asyncio.run(monitor_crawl())
    except KeyboardInterrupt:
        print(f"\nMonitor stopped at {get_timestamp()}")
    finally:
        print("Shutting down...")


if __name__ == "__main__":
    main()

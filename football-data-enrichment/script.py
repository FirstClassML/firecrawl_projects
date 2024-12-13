from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import pandas as pd


class StadiumInfo(BaseModel):
    name: str = Field(description="The name of the football stadium")
    capacity: int = Field(description="Stadium capacity at the time")
    surface: str = Field(description="Type of playing surface")
    built_year: int = Field(description="Year the stadium was built")


class WeatherData(BaseModel):
    temperature: float = Field(description="Temperature in Celsius on this day")
    precipitation: float = Field(description="Precipitation in mm")
    conditions: str = Field(description="Weather conditions description")


def enrich_match_data(row):
    app = FirecrawlApp()

    # Format search query for weather data
    date = row["date"]
    city = row["city"]
    weather_url = f"https://www.wunderground.com/history/{city}/{date}"

    # Get historical weather data
    weather_data = app.scrape_url(
        weather_url,
        params={
            "formats": ["extract"],
            "extract": {"schema": WeatherData.model_json_schema()},
        },
    )

    return weather_data


if __name__ == "__main__":
    df = pd.read_csv("data/results.csv")
    for row in df.iterrows():
        data = enrich_match_data(row)
        print(data)
        break

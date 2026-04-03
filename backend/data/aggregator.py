import asyncio
import time
import logging
from .rent import get_rent_data
from .air_quality import fetch_aqi
from .crime import fetch_crime
from .noise import fetch_noise
from .crowd import get_crowd_data
from .sentiment import get_sentiment_data

logger = logging.getLogger(__name__)


async def build_city_snapshot(city: str) -> dict:
    """Fetch all data sources concurrently and merge into a single snapshot."""
    rent_data = get_rent_data(city)
    crowd_data = get_crowd_data(city)
    sentiment_data = get_sentiment_data(city)

    aqi_data, crime_data, noise_data = await asyncio.gather(
        fetch_aqi(city),
        fetch_crime(city),
        fetch_noise(city),
        return_exceptions=True,
    )

    # Handle exceptions from gather
    if isinstance(aqi_data, Exception):
        logger.error(f"AQI fetch error: {aqi_data}")
        aqi_data = {}
    if isinstance(crime_data, Exception):
        logger.error(f"Crime fetch error: {crime_data}")
        crime_data = {}
    if isinstance(noise_data, Exception):
        logger.error(f"Noise fetch error: {noise_data}")
        noise_data = {}

    districts = list(rent_data.keys())
    merged = {}

    for district in districts:
        rent = rent_data.get(district, {})
        aqi = aqi_data.get(district, {"aqi": 50, "normalized": 0.17})
        crime = crime_data.get(district, {"normalized": 0.3, "count_24h": 0, "felonies_24h": 0})
        noise = noise_data.get(district, {"normalized": 0.4, "complaints_24h": 0})
        crowd = crowd_data.get(district, {"normalized": 0.5})
        sentiment = sentiment_data.get(district, {"normalized": 0.6})

        merged[district] = {
            # Visual drivers
            "height_multiplier": rent.get("height_multiplier", 0.5),
            "lean": rent.get("lean", 0.2),
            "aqi": aqi.get("aqi", 50),
            "aqi_normalized": aqi.get("normalized", 0.17),
            "crime": crime.get("normalized", 0.3),
            "noise": noise.get("normalized", 0.4),
            "crowd": crowd.get("normalized", 0.5),
            "sentiment": sentiment.get("normalized", 0.6),
            # Raw stats for UI panel
            "rent": rent.get("rent", 0),
            "crime_count_24h": crime.get("count_24h", 0),
            "noise_complaints_24h": noise.get("complaints_24h", 0),
        }

    return {
        "city": city,
        "timestamp": int(time.time()),
        "districts": merged,
    }

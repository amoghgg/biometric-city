import httpx
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

NYC_311_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"

# District → approximate borough for 311 filtering
NYC_DISTRICT_BOROUGH = {
    "tribeca":      "MANHATTAN",
    "midtown":      "MANHATTAN",
    "lower_east":   "MANHATTAN",
    "harlem":       "MANHATTAN",
    "brooklyn":     "BROOKLYN",
    "queens":       "QUEENS",
    "bronx":        "BRONX",
    "williamsburg": "BROOKLYN",
    "astoria":      "QUEENS",
    "upper_west":   "MANHATTAN",
    "chelsea":      "MANHATTAN",
    "flushing":     "QUEENS",
}

MUMBAI_NOISE_BASE = {
    "bkc":          0.35,
    "bandra":       0.55,
    "colaba":       0.60,
    "andheri":      0.65,
    "dharavi":      0.50,
    "dadar":        0.70,
    "kurla":        0.60,
    "borivali":     0.40,
    "thane":        0.45,
    "lower_parel":  0.50,
}


async def fetch_noise(city: str) -> dict:
    if city == "nyc":
        return await _fetch_nyc_noise()
    return _simulate_mumbai_noise()


async def _fetch_nyc_noise() -> dict:
    since = (datetime.utcnow() - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%S")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                NYC_311_URL,
                params={
                    "$where": f"created_date >= '{since}' AND complaint_type LIKE '%Noise%'",
                    "$limit": 5000,
                    "$select": "borough,complaint_type",
                },
            )
            if resp.status_code == 200:
                complaints = resp.json()
                borough_counts = {}
                for c in complaints:
                    b = c.get("borough", "").upper()
                    borough_counts[b] = borough_counts.get(b, 0) + 1

                max_count = max(borough_counts.values()) if borough_counts else 1
                result = {}
                for district, borough in NYC_DISTRICT_BOROUGH.items():
                    count = borough_counts.get(borough, 0)
                    result[district] = {
                        "complaints_24h": count,
                        "normalized": round(min(count / max_count, 1.0), 3),
                    }
                return result
    except Exception as e:
        logger.warning(f"NYC 311 noise fetch failed: {e}")

    fallback = {"tribeca": 0.20, "midtown": 0.60, "lower_east": 0.55, "harlem": 0.50,
                "brooklyn": 0.45, "queens": 0.40, "bronx": 0.48, "williamsburg": 0.52,
                "astoria": 0.38, "upper_west": 0.35, "chelsea": 0.58, "flushing": 0.42}
    return {d: {"complaints_24h": 0, "normalized": v} for d, v in fallback.items()}


def _simulate_mumbai_noise() -> dict:
    import random
    import math
    hour = (datetime.utcnow().hour + 5.5) % 24
    day_factor = 0.4 + 0.6 * math.sin(math.pi * max(0, hour - 7) / 14) if 7 <= hour <= 21 else 0.3

    result = {}
    for district, base in MUMBAI_NOISE_BASE.items():
        jitter = random.uniform(-0.06, 0.06)
        normalized = max(0.0, min(1.0, base * day_factor + jitter))
        result[district] = {
            "complaints_24h": int(normalized * 120),
            "normalized": round(normalized, 3),
        }
    return result

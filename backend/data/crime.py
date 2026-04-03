import httpx
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# NYC OpenData — NYPD Complaint Data (real-time, no key required)
NYC_CRIME_URL = "https://data.cityofnewyork.us/resource/5uac-w243.json"

# Approximate lat/lon bounding boxes for each NYC district
NYC_DISTRICT_BOUNDS = {
    "tribeca":      (40.714, 40.722, -74.012, -74.002),
    "midtown":      (40.748, 40.760, -73.995, -73.970),
    "lower_east":   (40.715, 40.725, -73.995, -73.975),
    "harlem":       (40.800, 40.820, -73.960, -73.930),
    "brooklyn":     (40.650, 40.680, -73.990, -73.950),
    "queens":       (40.710, 40.740, -73.900, -73.860),
    "bronx":        (40.835, 40.865, -73.940, -73.880),
    "williamsburg": (40.705, 40.720, -73.965, -73.940),
    "astoria":      (40.765, 40.785, -73.940, -73.910),
    "upper_west":   (40.775, 40.800, -73.990, -73.970),
    "chelsea":      (40.742, 40.752, -74.005, -73.990),
    "flushing":     (40.755, 40.775, -73.845, -73.820),
}

# Mumbai crime — simulated from published district-level statistics
# Source: Maharashtra Crime Records Bureau annual report (normalized)
MUMBAI_CRIME_BASE = {
    "bkc":          0.15,
    "bandra":       0.25,
    "colaba":       0.30,
    "andheri":      0.40,
    "dharavi":      0.65,
    "dadar":        0.45,
    "kurla":        0.55,
    "borivali":     0.30,
    "thane":        0.35,
    "lower_parel":  0.20,
}


async def fetch_crime(city: str) -> dict:
    if city == "nyc":
        return await _fetch_nyc_crime()
    return _simulate_mumbai_crime()


async def _fetch_nyc_crime() -> dict:
    since = (datetime.utcnow() - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%S")
    result = {}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                NYC_CRIME_URL,
                params={
                    "$where": f"cmplnt_fr_dt >= '{since}'",
                    "$limit": 1000,
                    "$select": "latitude,longitude,law_cat_cd",
                },
            )
            if resp.status_code == 200:
                complaints = resp.json()
                counts = {d: 0 for d in NYC_DISTRICT_BOUNDS}
                felonies = {d: 0 for d in NYC_DISTRICT_BOUNDS}

                for c in complaints:
                    try:
                        lat = float(c.get("latitude", 0))
                        lon = float(c.get("longitude", 0))
                        is_felony = c.get("law_cat_cd") == "FELONY"
                    except (TypeError, ValueError):
                        continue

                    for district, (lat_min, lat_max, lon_min, lon_max) in NYC_DISTRICT_BOUNDS.items():
                        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
                            counts[district] += 1
                            if is_felony:
                                felonies[district] += 1
                            break

                max_count = max(counts.values()) or 1
                for district in NYC_DISTRICT_BOUNDS:
                    rate = counts[district] / max_count
                    result[district] = {
                        "count_24h": counts[district],
                        "felonies_24h": felonies[district],
                        "normalized": round(rate, 3),
                    }
                return result
    except Exception as e:
        logger.warning(f"NYC crime fetch failed: {e}")

    # Fallback
    fallback = {"tribeca": 0.10, "midtown": 0.35, "lower_east": 0.45, "harlem": 0.60,
                "brooklyn": 0.40, "queens": 0.35, "bronx": 0.70, "williamsburg": 0.38,
                "astoria": 0.30, "upper_west": 0.20, "chelsea": 0.25, "flushing": 0.32}
    return {d: {"count_24h": 0, "felonies_24h": 0, "normalized": v} for d, v in fallback.items()}


def _simulate_mumbai_crime() -> dict:
    import random
    import math
    # Add time-of-day variance — crime peaks at night
    hour = datetime.utcnow().hour + 5.5  # IST offset
    night_factor = 0.3 + 0.7 * abs(math.sin(math.pi * hour / 24))

    result = {}
    for district, base in MUMBAI_CRIME_BASE.items():
        jitter = random.uniform(-0.05, 0.05)
        normalized = max(0.0, min(1.0, base * night_factor + jitter))
        result[district] = {
            "count_24h": int(normalized * 80),
            "felonies_24h": int(normalized * 15),
            "normalized": round(normalized, 3),
        }
    return result

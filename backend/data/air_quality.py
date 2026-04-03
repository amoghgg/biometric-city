import httpx
import logging

logger = logging.getLogger(__name__)

# OpenAQ v2 API — no key required
# Query by city name, get latest PM2.5 readings
NYC_CITY_QUERY = "New York"
MUMBAI_CITY_QUERY = "Mumbai"

# District → station name substring for matching
NYC_STATION_MAP = {
    "tribeca":      "Manhattan",
    "midtown":      "Manhattan",
    "lower_east":   "Manhattan",
    "harlem":       "Manhattan",
    "brooklyn":     "Brooklyn",
    "queens":       "Queens",
    "bronx":        "Bronx",
    "williamsburg": "Brooklyn",
    "astoria":      "Queens",
    "upper_west":   "Manhattan",
    "chelsea":      "Manhattan",
    "flushing":     "Queens",
}

MUMBAI_STATION_MAP = {
    "bkc":          "Bandra",
    "bandra":       "Bandra",
    "colaba":       "Colaba",
    "andheri":      "Andheri",
    "dharavi":      "Sion",
    "dadar":        "Dadar",
    "kurla":        "Kurla",
    "borivali":     "Borivali",
    "thane":        "Thane",
    "lower_parel":  "Worli",
}

# Fallback AQI values if API fails
NYC_FALLBACK = {
    "tribeca": 42, "midtown": 48, "lower_east": 55, "harlem": 58,
    "brooklyn": 45, "queens": 52, "bronx": 68, "williamsburg": 47,
    "astoria": 50, "upper_west": 44, "chelsea": 46, "flushing": 54,
}

MUMBAI_FALLBACK = {
    "bkc": 120, "bandra": 135, "colaba": 118, "andheri": 155,
    "dharavi": 185, "dadar": 148, "kurla": 165, "borivali": 130,
    "thane": 142, "lower_parel": 125,
}


async def fetch_aqi(city: str) -> dict:
    fallback = NYC_FALLBACK if city == "nyc" else MUMBAI_FALLBACK
    station_map = NYC_STATION_MAP if city == "nyc" else MUMBAI_STATION_MAP
    city_query = NYC_CITY_QUERY if city == "nyc" else MUMBAI_CITY_QUERY

    area_aqi = {}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://api.openaq.org/v2/latest",
                params={
                    "city": city_query,
                    "parameter": "pm25",
                    "limit": 100,
                },
                headers={"accept": "application/json"},
            )
            if resp.status_code == 200:
                data = resp.json()
                for loc in data.get("results", []):
                    loc_name = loc.get("location", "")
                    for m in loc.get("measurements", []):
                        if m.get("parameter") == "pm25" and m.get("value", 0) > 0:
                            aqi = _pm25_to_aqi(m["value"])
                            # Match to area keyword
                            for area, keyword in station_map.items():
                                if keyword.lower() in loc_name.lower():
                                    area_aqi[area] = aqi
    except Exception as e:
        logger.warning(f"OpenAQ v2 fetch failed for {city}: {e}")

    result = {}
    for district in station_map:
        aqi = area_aqi.get(district, fallback.get(district, 50))
        result[district] = {
            "aqi": aqi,
            "normalized": round(min(aqi / 300, 1.0), 3),
        }

    return result


def _pm25_to_aqi(pm25: float) -> int:
    breakpoints = [
        (0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 500.4, 301, 500),
    ]
    for low_pm, high_pm, low_aqi, high_aqi in breakpoints:
        if low_pm <= pm25 <= high_pm:
            aqi = ((high_aqi - low_aqi) / (high_pm - low_pm)) * (pm25 - low_pm) + low_aqi
            return int(aqi)
    return 500

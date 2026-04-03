import math
import random
from datetime import datetime


# Simulated sentiment with realistic daily arc
# Cities have different emotional rhythms — NYC is more volatile, Mumbai is resilient

NYC_DISTRICT_SENTIMENT_BASE = {
    "tribeca":      0.62,
    "midtown":      0.50,
    "lower_east":   0.55,
    "harlem":       0.58,
    "brooklyn":     0.65,
    "queens":       0.60,
    "bronx":        0.48,
    "williamsburg": 0.70,
    "astoria":      0.63,
    "upper_west":   0.68,
    "chelsea":      0.72,
    "flushing":     0.58,
}

MUMBAI_DISTRICT_SENTIMENT_BASE = {
    "bkc":          0.60,
    "bandra":       0.72,
    "colaba":       0.65,
    "andheri":      0.55,
    "dharavi":      0.52,
    "dadar":        0.58,
    "kurla":        0.50,
    "borivali":     0.62,
    "thane":        0.60,
    "lower_parel":  0.65,
}


def get_sentiment_data(city: str) -> dict:
    bases = NYC_DISTRICT_SENTIMENT_BASE if city == "nyc" else MUMBAI_DISTRICT_SENTIMENT_BASE
    hour_offset = -5 if city == "nyc" else 5.5
    local_hour = (datetime.utcnow().hour + hour_offset) % 24

    # Sentiment arc: lowest at 3-5am (fatigue/anxiety), peaks at 10am and 7pm
    morning_peak = math.exp(-0.5 * ((local_hour - 10) / 3.0) ** 2) * 0.15
    evening_peak = math.exp(-0.5 * ((local_hour - 19) / 2.5) ** 2) * 0.12
    night_dip = -0.15 if 1 <= local_hour <= 5 else 0
    time_modifier = morning_peak + evening_peak + night_dip

    result = {}
    for district, base in bases.items():
        jitter = random.uniform(-0.03, 0.03)
        normalized = max(0.0, min(1.0, base + time_modifier + jitter))
        result[district] = {
            "normalized": round(normalized, 3),
        }
    return result

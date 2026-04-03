import math
from datetime import datetime


# Time-of-day crowd curves per district type
# Peak hours differ: financial = 9-6, nightlife = 9pm-2am, residential = 7-9am + 5-7pm

DISTRICT_TYPES = {
    # NYC
    "tribeca":      "financial",
    "midtown":      "transit_hub",
    "lower_east":   "nightlife",
    "harlem":       "residential",
    "brooklyn":     "residential",
    "queens":       "residential",
    "bronx":        "residential",
    "williamsburg": "nightlife",
    "astoria":      "residential",
    "upper_west":   "residential",
    "chelsea":      "nightlife",
    "flushing":     "commercial",
    # Mumbai
    "bkc":          "financial",
    "bandra":       "nightlife",
    "colaba":       "tourist",
    "andheri":      "transit_hub",
    "dharavi":      "industrial",
    "dadar":        "transit_hub",
    "kurla":        "transit_hub",
    "borivali":     "residential",
    "thane":        "residential",
    "lower_parel":  "commercial",
}

# Mumbai peak train hours amplify crowd
MUMBAI_TRAIN_PEAKS = [8.0, 9.0, 18.0, 19.0, 20.0]


def _crowd_curve(hour: float, district_type: str, city: str) -> float:
    """Returns 0–1 crowd density for a given hour and district type."""

    if district_type == "financial":
        # Sharp 9-6 peak, dead at night
        if 9 <= hour <= 18:
            x = (hour - 9) / 9
            return 0.5 + 0.5 * math.sin(math.pi * x)
        return 0.05

    elif district_type == "transit_hub":
        # Double peak: morning + evening commute
        morning = math.exp(-0.5 * ((hour - 8.5) / 1.2) ** 2)
        evening = math.exp(-0.5 * ((hour - 18.5) / 1.5) ** 2)
        base = max(morning, evening)
        # Mumbai trains are more intense
        if city == "mumbai":
            base = min(base * 1.3, 1.0)
        return max(base, 0.1)

    elif district_type == "nightlife":
        # Low during day, ramps up 7pm–2am
        if hour >= 19 or hour <= 2:
            h = hour if hour >= 19 else hour + 24
            x = (h - 19) / 7
            return 0.3 + 0.65 * math.sin(math.pi * x * 0.85)
        elif 7 <= hour <= 19:
            return 0.15 + 0.1 * math.sin(math.pi * (hour - 7) / 12)
        return 0.1

    elif district_type == "residential":
        # Two humps: morning rush + evening return
        morning = math.exp(-0.5 * ((hour - 8) / 1.0) ** 2) * 0.7
        evening = math.exp(-0.5 * ((hour - 17.5) / 1.2) ** 2) * 0.8
        night = 0.1 if 22 <= hour or hour <= 5 else 0.25
        return max(morning, evening, night)

    elif district_type == "commercial":
        if 10 <= hour <= 21:
            x = (hour - 10) / 11
            return 0.4 + 0.5 * math.sin(math.pi * x)
        return 0.1

    elif district_type == "industrial":
        if 6 <= hour <= 18:
            return 0.5 + 0.3 * math.sin(math.pi * (hour - 6) / 12)
        return 0.15

    elif district_type == "tourist":
        if 10 <= hour <= 22:
            x = (hour - 10) / 12
            return 0.35 + 0.55 * math.sin(math.pi * x)
        return 0.1

    return 0.2


def get_crowd_data(city: str) -> dict:
    import random
    now = datetime.utcnow()
    # Offset for local time
    hour_offset = -5 if city == "nyc" else 5.5
    local_hour = (now.hour + hour_offset) % 24

    districts = {k: v for k, v in DISTRICT_TYPES.items()
                 if k in (_nyc_districts() if city == "nyc" else _mumbai_districts())}

    result = {}
    for district, dtype in districts.items():
        base = _crowd_curve(local_hour, dtype, city)
        jitter = random.uniform(-0.04, 0.04)
        normalized = max(0.0, min(1.0, base + jitter))
        result[district] = {
            "normalized": round(normalized, 3),
            "local_hour": round(local_hour, 1),
        }
    return result


def _nyc_districts():
    return ["tribeca", "midtown", "lower_east", "harlem", "brooklyn",
            "queens", "bronx", "williamsburg", "astoria", "upper_west", "chelsea", "flushing"]

def _mumbai_districts():
    return ["bkc", "bandra", "colaba", "andheri", "dharavi",
            "dadar", "kurla", "borivali", "thane", "lower_parel"]

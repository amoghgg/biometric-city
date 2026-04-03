# Static rent/property value data per district
# NYC: median monthly rent (USD), Mumbai: median monthly rent (INR thousands)
# Normalized 0–1 for building height multiplier

NYC_RENT = {
    "tribeca":       {"rent": 5800, "rent_change": 0.18},
    "midtown":       {"rent": 4900, "rent_change": 0.12},
    "lower_east":    {"rent": 3800, "rent_change": 0.25},
    "harlem":        {"rent": 2600, "rent_change": 0.38},
    "brooklyn":      {"rent": 3200, "rent_change": 0.30},
    "queens":        {"rent": 2400, "rent_change": 0.20},
    "bronx":         {"rent": 1800, "rent_change": 0.15},
    "williamsburg":  {"rent": 3600, "rent_change": 0.42},
    "astoria":       {"rent": 2800, "rent_change": 0.22},
    "upper_west":    {"rent": 4200, "rent_change": 0.08},
    "chelsea":       {"rent": 4600, "rent_change": 0.14},
    "flushing":      {"rent": 2200, "rent_change": 0.16},
}

MUMBAI_RENT = {
    "bkc":           {"rent": 180, "rent_change": 0.22},
    "bandra":        {"rent": 150, "rent_change": 0.28},
    "colaba":        {"rent": 160, "rent_change": 0.10},
    "andheri":       {"rent": 90,  "rent_change": 0.30},
    "dharavi":       {"rent": 25,  "rent_change": 0.45},
    "dadar":         {"rent": 80,  "rent_change": 0.20},
    "kurla":         {"rent": 55,  "rent_change": 0.35},
    "borivali":      {"rent": 65,  "rent_change": 0.18},
    "thane":         {"rent": 50,  "rent_change": 0.25},
    "lower_parel":   {"rent": 140, "rent_change": 0.32},
}


def get_rent_data(city: str) -> dict:
    data = NYC_RENT if city == "nyc" else MUMBAI_RENT
    max_rent = max(v["rent"] for v in data.values())
    return {
        district: {
            **vals,
            "height_multiplier": round(vals["rent"] / max_rent, 3),
            "lean": round(min(vals["rent_change"] * 2, 1.0), 3),
        }
        for district, vals in data.items()
    }

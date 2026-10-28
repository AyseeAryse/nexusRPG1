"""Compatibility helpers for geographic location data.

A location's *country* is a geographic level, not a citizenship or an alliance.
Only Earth -> Japan -> Tokyo is explicitly mapped at present; do not infer
unapproved political borders for other settlements.
"""
from typing import Dict, Optional


TOKYO_CITY_ALIASES = frozenset({"Токио", "Нью-Токио"})


def normalize_location(location: Dict, previous: Optional[Dict] = None) -> Dict:
    """Ensure a location includes country without inventing unknown borders.

    Current/new legacy Tokyo maps to Japan. Other locations use an explicit
    country if present, or retain the previous one only for the same city on
    the same celestial body. None means "not established", not "stateless".
    """
    result = dict(location)
    if result.get("planet") == "Земля" and result.get("city") in TOKYO_CITY_ALIASES:
        result["country"] = "Япония"
    elif "country" not in result:
        unchanged_city = (
            previous is not None
            and previous.get("planet") == result.get("planet")
            and previous.get("city") == result.get("city")
        )
        result["country"] = previous.get("country") if unchanged_city else None
    return result


def merge_location(current: Dict, changes: Dict) -> Dict:
    """Apply a partial location change without carrying a stale country.

    A planet/city change invalidates the old country unless the caller
    explicitly supplies a new one. District/place changes preserve it.
    """
    result = dict(current)
    result.update(changes)
    planet_changed = result.get("planet") != current.get("planet")
    city_changed = result.get("city") != current.get("city")

    # A partial AI location update must not carry Tokyo's district to Mars,
    # or the industrial district of one city into another city.
    if planet_changed:
        for key in ("city", "district", "place"):
            if key not in changes:
                result[key] = ""
    elif city_changed:
        for key in ("district", "place"):
            if key not in changes:
                result[key] = ""
    elif result.get("district") != current.get("district") and "place" not in changes:
        result["place"] = ""

    if (planet_changed or city_changed) and "country" not in changes:
        result.pop("country", None)
    return normalize_location(result, previous=current)

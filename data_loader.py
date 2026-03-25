import json
import os
from typing import Optional

DATA_FILE = os.path.join(os.path.dirname(__file__), "mock.json")


def load_mock_data() -> dict:
    """Load fuel station data from mock.json."""
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_all_stations(data: Optional[dict] = None) -> list[dict]:
    """Get a flat list of all stations from mock data."""
    if data is None:
        data = load_mock_data()

    stations = []
    for city_entry in data.get("cities", []):
        city_name = city_entry["city"]
        voivodeship = city_entry.get("voivodeship", "")
        for station in city_entry.get("stations", []):
            stations.append({
                **station,
                "city": city_name,
                "voivodeship": voivodeship,
            })
    return stations


def get_stations_by_city(city: str, data: Optional[dict] = None) -> list[dict]:
    """Get stations filtered by city name (case-insensitive partial match)."""
    all_stations = get_all_stations(data)
    city_lower = city.lower()
    return [s for s in all_stations if city_lower in s["city"].lower()]


def get_stations_by_voivodeship(voivodeship: str, data: Optional[dict] = None) -> list[dict]:
    """Get stations filtered by voivodeship (case-insensitive partial match)."""
    all_stations = get_all_stations(data)
    v_lower = voivodeship.lower()
    return [s for s in all_stations if v_lower in s.get("voivodeship", "").lower()]


def get_all_cities(data: Optional[dict] = None) -> list[str]:
    """Get list of all available cities."""
    if data is None:
        data = load_mock_data()
    return [c["city"] for c in data.get("cities", [])]


def get_all_voivodeships(data: Optional[dict] = None) -> list[str]:
    """Get unique list of voivodeships."""
    if data is None:
        data = load_mock_data()
    return list(set(c.get("voivodeship", "") for c in data.get("cities", []) if c.get("voivodeship")))


def get_all_brands(data: Optional[dict] = None) -> list[str]:
    """Get unique list of station brands."""
    stations = get_all_stations(data)
    return sorted(set(s.get("brand", "") for s in stations if s.get("brand")))

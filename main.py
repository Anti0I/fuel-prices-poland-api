import math
import logging
from typing import Optional

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os

from data_loader import load_mock_data, get_all_stations, get_stations_by_city, get_all_cities, get_stations_by_voivodeship, get_all_voivodeships, get_all_brands

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ---------- Haversine ----------
def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# ---------- App ----------
app = FastAPI(
    title="Paliwo API",
    description="Fuel price aggregator for Poland - Pure JSON API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load mock data once at startup
mock_data = load_mock_data()
logger.info(f"Loaded mock data: {len(get_all_stations(mock_data))} stations in {len(get_all_cities(mock_data))} cities")

# ---------- API Endpoints ----------
@app.get("/", tags=["info"])
async def root():
    """API info and status."""
    all_stations = get_all_stations(mock_data)
    return {
        "name": "Paliwo API",
        "version": "1.0.0",
        "description": "Fuel price aggregator for Poland",
        "total_stations": len(all_stations),
        "updated_at": mock_data.get("updated_at"),
        "endpoints": [
            "/stations (advanced search)",
            "/stations/near (haversine search)",
            "/filters (available filter options)"
        ]
    }


@app.get("/filters", tags=["info"])
async def available_filters():
    """Get all available filter options (cities, voivodeships, brands)."""
    return {
        "cities": sorted(get_all_cities(mock_data)),
        "voivodeships": sorted(get_all_voivodeships(mock_data)),
        "brands": get_all_brands(mock_data),
    }


@app.get("/api/walkthrough", response_class=HTMLResponse, tags=["info"])
async def api_walkthrough():
    """Read API usage instructions from the walkthrough file."""
    walkthrough_path = os.path.join(os.path.dirname(__file__), "walkthrough.md")
    if os.path.exists(walkthrough_path):
        with open(walkthrough_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Escape HTML characters slightly
        content = content.replace("<", "&lt;").replace(">", "&gt;")
        html = f"""
        <html>
        <head>
            <title>Paliwo API Walkthrough</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; line-height: 1.6; max-width: 900px; margin: 0 auto; }}
                pre {{ background: #1e293b; padding: 20px; border-radius: 8px; overflow-x: auto; font-family: 'Cascadia Code', Consolas, monospace; white-space: pre-wrap; }}
                h1, h2, h3 {{ color: #3b82f6; }}
                a {{ color: #60a5fa; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <h1>Paliwo API — Dokumentacja</h1>
            <p>Poniżej znajdziesz treść dokumentacji technicznej wygenerowanej przez Asystenta (walkthrough.md):</p>
            <pre>{content}</pre>
        </body>
        </html>
        """
        return html
    return "<h1>Dokumentacja nie została znaleziona.</h1>"


@app.get("/stations", tags=["stations"])
async def advanced_search(
    city: Optional[str] = Query(None, description="Filter by city name"),
    voivodeship: Optional[str] = Query(None, description="Filter by voivodeship"),
    brand: Optional[str] = Query(None, description="Filter by station brand"),
    fuel: Optional[str] = Query(None, description="Require a specific fuel type (pb95, diesel, lpg)"),
    sort_by: Optional[str] = Query(None, description="Sort results ('price_asc', 'price_desc', 'name')"),
):
    """
    Advanced search endpoint.
    Allows filtering by city, voivodeship, brand, and sorting by price for a specific fuel type.
    """
    stations = get_all_stations(mock_data)

    # 1. Apply Filters
    if city:
        city_lower = city.lower()
        stations = [s for s in stations if city_lower in s["city"].lower()]
        
    if voivodeship:
        v_lower = voivodeship.lower()
        stations = [s for s in stations if v_lower in s.get("voivodeship", "").lower()]
        
    if brand:
        b_lower = brand.lower()
        stations = [s for s in stations if b_lower == s["brand"].lower()]
        
    if fuel:
        stations = [s for s in stations if fuel in s.get("prices", {})]

    # 2. Apply Sorting
    if sort_by and fuel:
        if sort_by == "price_asc":
            stations.sort(key=lambda s: s["prices"].get(fuel, float('inf')))
        elif sort_by == "price_desc":
            stations.sort(key=lambda s: s["prices"].get(fuel, 0), reverse=True)
    elif sort_by == "name":
        stations.sort(key=lambda s: s["name"])

    return {
        "count": len(stations),
        "currency": mock_data.get("currency", "PLN"),
        "stations": stations,
    }


@app.get("/stations/near", tags=["stations"])
async def nearby_stations(
    lat: float = Query(..., description="Latitude of search center"),
    lng: float = Query(..., description="Longitude of search center"),
    radius: float = Query(10.0, description="Search radius in km"),
    limit: int = Query(50, description="Max number of results"),
):
    """
    Find stations within a radius (km) of a given coordinate.
    Uses Haversine formula for distance calculation.
    """
    all_stations = get_all_stations(mock_data)
    nearby = []
    for s in all_stations:
        dist = haversine_km(lat, lng, s["lat"], s["lng"])
        if dist <= radius:
            nearby.append({
                **s,
                "distance_km": round(dist, 2),
            })

    nearby.sort(key=lambda x: x["distance_km"])
    return {
        "count": len(nearby[:limit]),
        "stations": nearby[:limit],
    }

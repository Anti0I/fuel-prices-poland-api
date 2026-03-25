# Fuel Price Aggregator MVP — Pure API

## What Was Built

A fast, lightweight JSON API for finding and comparing fuel prices in Poland. It features advanced filtering (by city, voivodeship, brand, fuel type) and a geospatial search feature to find stations near you, powered by a FastAPI backend serving mock data.

## Project Structure

```
paliwo/
├── main.py             # FastAPI app with endpoints
├── data_loader.py      # Data loading and filtering logic
├── mock.json           # Mock fuel station data with voivodeships
├── requirements.txt    # fastapi, uvicorn
└── .gitignore          # Ignored files
```

## Pure JSON API Usage

You can use the API directly via HTTP requests with query parameters.

### `GET /stations`

Returns filtered and sorted fuel stations in JSON format.

**Available Query Parameters:**
- `city` (string): Filter by city name (e.g., `Warszawa`)
- `voivodeship` (string): Filter by voivodeship (e.g., `mazowieckie`)
- `brand` (string): Filter by station brand (e.g., `Orlen`)
- `fuel` (string): Require specific fuel type (`pb95`, `diesel`, `lpg`)
- `sort_by` (string): Sort results (`price_asc`, `price_desc`, `name`)

**Examples:**
- `http://127.0.0.1:8000/stations?city=Warszawa&fuel=pb95&sort_by=price_asc` (Cheapest PB95 in Warsaw)
- `http://127.0.0.1:8000/stations?brand=Shell&fuel=diesel` (All Shell stations with Diesel)

### `GET /stations/near`

Finds stations near coordinates using the Haversine formula.

**Available Query Parameters:**
- `lat` (float): Latitude (required)
- `lng` (float): Longitude (required)
- `radius` (float): Search radius in km (default: 10)
- `limit` (int): Max results (default: 50)

**Example:**
- `http://127.0.0.1:8000/stations/near?lat=52.23&lng=21.01&radius=5`

### `GET /filters`

Retrieves a list of all available filtering options (distinct cities, voivodeships, and brands) existing in the dataset.

## Quick Start

1. **Run the server**:
   ```bash
   python -m uvicorn main:app --reload
   ```
2. **Access the API using curl or your browser**:
   `curl http://127.0.0.1:8000/stations?city=Warsaw`
   `curl http://127.0.0.1:8000/filters`
   
Or just visit the interactive Swagger UI documentation at:
`http://127.0.0.1:8000/docs`

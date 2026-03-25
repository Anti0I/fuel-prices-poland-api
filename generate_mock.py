import json
import random
from datetime import datetime, timezone

cities_data = [
    {
        "city": "Warszawa",
        "voivodeship": "mazowieckie",
        "center": (52.2297, 21.0122),
        "radius_deg": 0.1,  # roughly 10km
        "stations_count": 25
    },
    {
        "city": "Kraków",
        "voivodeship": "małopolskie",
        "center": (50.0647, 19.9450),
        "radius_deg": 0.08,
        "stations_count": 20
    },
    {
        "city": "Gdańsk",
        "voivodeship": "pomorskie",
        "center": (54.3520, 18.6466),
        "radius_deg": 0.07,
        "stations_count": 15
    },
    {
        "city": "Wrocław",
        "voivodeship": "dolnośląskie",
        "center": (51.1079, 17.0385),
        "radius_deg": 0.08,
        "stations_count": 18
    },
    {
        "city": "Poznań",
        "voivodeship": "wielkopolskie",
        "center": (52.4064, 16.9252),
        "radius_deg": 0.07,
        "stations_count": 15
    },
    {
        "city": "Łódź",
        "voivodeship": "łódzkie",
        "center": (51.7592, 19.4560),
        "radius_deg": 0.08,
        "stations_count": 18
    },
    {
        "city": "Szczecin",
        "voivodeship": "zachodniopomorskie",
        "center": (53.4285, 14.5528),
        "radius_deg": 0.07,
        "stations_count": 12
    },
]

brands = ["Orlen", "Shell", "BP", "Circle K", "Moya", "Amic", "MOL"]

base_prices = {
    "pb95": 6.35,
    "diesel": 6.50,
    "lpg": 3.05
}

def generate_stations():
    result = {
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:00:00Z"),
        "currency": "PLN",
        "unit": "per_liter",
        "cities": []
    }
    
    for c_data in cities_data:
        city_entry = {
            "city": c_data["city"],
            "voivodeship": c_data["voivodeship"],
            "stations": []
        }
        
        for i in range(c_data["stations_count"]):
            brand = random.choice(brands)
            
            # Generate random offset from center
            lat_offset = random.uniform(-c_data["radius_deg"], c_data["radius_deg"])
            lng_offset = random.uniform(-c_data["radius_deg"], c_data["radius_deg"])
            
            lat = round(c_data["center"][0] + lat_offset, 6)
            lng = round(c_data["center"][1] + lng_offset, 6)
            
            # Generate random prices around base
            price_variance = random.uniform(-0.15, 0.20)
            prices = {
                "pb95": round(base_prices["pb95"] + price_variance, 2),
                "diesel": round(base_prices["diesel"] + price_variance, 2),
            }
            if random.random() > 0.1: # 90% have LPG
                 prices["lpg"] = round(base_prices["lpg"] + random.uniform(-0.1, 0.1), 2)
                 
            # Name modifiers based on brand or location
            modifiers = ["Centrum", "Północ", "Południe", "Wschód", "Zachód", "Express", f"ul. {random.randint(1, 150)}"]
            name = f"{brand} {random.choice(modifiers)}"
            
            station = {
                "name": name,
                "brand": brand,
                "lat": lat,
                "lng": lng,
                "prices": prices,
                "updated_at": result["updated_at"]
            }
            city_entry["stations"].append(station)
            
        result["cities"].append(city_entry)
        
    return result

if __name__ == "__main__":
    data = generate_stations()
    with open("mock.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("mock.json updated with generated data.")

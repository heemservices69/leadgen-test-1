"""Source: OpenStreetMap, worldwide, free, no key.
Nominatim (geocoding) + Overpass (business search). Both are public/free; keep usage polite."""
import requests
from config import USER_AGENT

NOMINATIM = "https://nominatim.openstreetmap.org/search"
OVERPASS_SERVERS = ["https://overpass-api.de/api/interpreter",
                    "https://overpass.kumi.systems/api/interpreter"]
HEADERS = {"User-Agent": USER_AGENT}

CATEGORIES = {
    "restaurant / cafe": ["amenity=restaurant", "amenity=cafe", "amenity=fast_food"],
    "salon / beauty": ["shop=hairdresser", "shop=beauty"],
    "gym / fitness": ["leisure=fitness_centre"],
    "clinic / dentist": ["amenity=clinic", "amenity=dentist", "amenity=doctors"],
    "school / academy": ["amenity=school", "amenity=college", "office=educational_institution"],
    "hotel / guest house": ["tourism=hotel", "tourism=guest_house"],
    "clothing / retail": ["shop=clothes", "shop=boutique", "shop=shoes"],
    "real estate": ["office=estate_agent"],
    "car services": ["shop=car_repair", "shop=car"],
    "lawyer / accountant": ["office=lawyer", "office=accountant"],
    "bakery / grocery": ["shop=bakery", "shop=supermarket", "shop=convenience"],
}

def geocode(place: str) -> dict:
    r = requests.get(NOMINATIM, params={"q": place, "format": "jsonv2", "limit": 1},
                     headers=HEADERS, timeout=30)
    r.raise_for_status()
    res = r.json()
    if not res:
        raise ValueError(f"Place not found: {place}")
    x = res[0]
    base = {"relation": 3600000000, "way": 2400000000}.get(x["osm_type"])
    return {"lat": float(x["lat"]), "lon": float(x["lon"]),
            "area_id": base + int(x["osm_id"]) if base else None,
            "label": x["display_name"].split(",")[0]}

def search(place: str, category: str, limit: int = 100, radius_km: float = 0):
    """place: any city/region/country/neighbourhood on Earth.
    radius_km > 0 -> search that radius around the place centre (good for big cities)."""
    tags = CATEGORIES.get(category) or [t.strip() for t in category.split(",")]
    g = geocode(place)
    if radius_km > 0 or not g["area_id"]:
        scope, head = f"(around:{int((radius_km or 5) * 1000)},{g['lat']},{g['lon']})", ""
    else:
        scope, head = "(area.a)", f"area({g['area_id']})->.a;"
    parts = "".join(f'nwr["{t.split("=")[0]}"="{t.split("=")[1]}"]{scope};'
                    for t in tags if "=" in t)
    q = f"[out:json][timeout:90];{head}({parts});out center tags {limit};"
    data, err = None, None
    for url in OVERPASS_SERVERS:
        try:
            r = requests.post(url, data={"data": q}, headers=HEADERS, timeout=120)
            r.raise_for_status()
            data = r.json()
            break
        except Exception as e:
            err = e
    if data is None:
        raise RuntimeError(f"Map servers busy, try a smaller area. ({err})")
    out = []
    for el in data.get("elements", []):
        t = el.get("tags", {})
        if not t.get("name"):
            continue
        c = el.get("center", el)
        lat, lon = c.get("lat"), c.get("lon")
        addr = " ".join(filter(None, [t.get("addr:housenumber"), t.get("addr:street"),
                                      t.get("addr:suburb"), t.get("addr:city")]))
        out.append({
            "name": t["name"], "category": category, "city": g["label"], "address": addr,
            "phone": t.get("phone") or t.get("contact:phone", ""),
            "email": t.get("email") or t.get("contact:email", ""),
            "website": t.get("website") or t.get("contact:website", ""),
            "facebook": t.get("contact:facebook", ""), "instagram": t.get("contact:instagram", ""),
            "maps_link": f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=18/{lat}/{lon}" if lat else "",
            "lat": lat, "lon": lon, "source": "OpenStreetMap",
        })
    return out

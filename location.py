import json
import urllib.request

def ip_location():
    url = "https://ipapi.co/json/"
    with urllib.request.urlopen(url, timeout=10) as r:
        data = json.loads(r.read().decode("utf-8"))
    return {
        "city": data.get("city"),
        "lat": data.get("latitude"),
        "lon": data.get("longitude"),
    }
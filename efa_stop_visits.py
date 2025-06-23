import requests


def fetch_stop_visits(stop_id: str) -> dict:
    """Return JSON data for upcoming visits at a stop from the EFA VRR API."""
    url = "https://efa.vrr.de/standard/XML_STOPVISIT_REQUEST"
    params = {
        "language": "de",
        "outputFormat": "JSON",
        "coordOutputFormat": "WGS84[DD.ddddd]",
        "siteid": "VRR",
        "stop": stop_id,
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def show_active_vehicles(data: dict) -> None:
    """Print information about all active vehicles in the response."""
    visits = data.get("stopVisits", [])
    for visit in visits:
        journey = visit.get("monitoredVehicleJourney", {})
        call = journey.get("monitoredCall", {})
        location = journey.get("vehicleLocation", {})
        print(
            f"Linie {journey.get('lineRef')} | Kurs {journey.get('courseOfJourneyRef')}"
        )
        print(f"Richtung: {journey.get('directionName')}")
        print(f"Haltestelle: {call.get('stopPointRef')}")
        print(
            f"Geoposition: {location.get('latitude')}, {location.get('longitude')}"
        )
        print(f"Geplante Ankunft: {call.get('aimedArrivalTime')}")
        print("-" * 40)


if __name__ == "__main__":
    # Example stop: Franziskanerstra\u00dfe Essen
    stop_id = "de:05113:7056"
    data = fetch_stop_visits(stop_id)
    show_active_vehicles(data)

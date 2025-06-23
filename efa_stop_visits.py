import requests


def fetch_visits_by_name(name: str) -> None:
    """Fetch and display stop visits using a stop name."""
    url = "https://efa.vrr.de/standard/XML_STOPVISIT_REQUEST"
    params = {
        "language": "de",
        "outputFormat": "JSON",
        "coordOutputFormat": "WGS84[DD.ddddd]",
        "name": name,  # Kein stop=, sondern name=
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        visits = data.get("stopVisits", [])
        if not visits:
            print("Keine Fahrzeugdaten vorhanden.")
            return
        for v in visits:
            j = v["monitoredVehicleJourney"]
            print(f"Linie {j['lineRef']} | Kurs {j.get('courseOfJourneyRef')}")
            print(f"Richtung: {j.get('directionName')}")
            print(f"Haltestelle: {j['monitoredCall']['stopPointRef']}")
            print(f"Geoposition: {j.get('vehicleLocation', {})}")
            print("-" * 40)
    except requests.HTTPError as e:
        print("Fehler beim Abruf:", e)


if __name__ == "__main__":
    # Beispiel
    fetch_visits_by_name("Franziskanerstr")

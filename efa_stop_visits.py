import requests


# Essen tram lines shown by default
ESSEN_LINES = {"101", "103", "105", "106", "107", "108", "109"}


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
            line = str(j.get("lineRef"))
            if line not in ESSEN_LINES:
                continue
            stop_call = j.get("monitoredCall", {})
            stop_name = stop_call.get("stopPointName") or stop_call.get(
                "stopPointRef"
            )
            print(f"Linie {line} | Kurs {j.get('courseOfJourneyRef')}")
            print(f"Richtung: {j.get('directionName')}")
            print(f"Haltestelle: {stop_name}")
            print(f"Geoposition: {j.get('vehicleLocation', {})}")
            print("-" * 40)
    except requests.HTTPError as e:
        print("Fehler beim Abruf:", e)


if __name__ == "__main__":
    # Beispiel
    fetch_visits_by_name("Franziskanerstr")

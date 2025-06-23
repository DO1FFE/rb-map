import datetime
import json
from typing import List, Dict, Optional, Tuple

import requests


def fetch_city_stops(city_name: str) -> List[str]:
    """Return a list of stop IDs for the given city name."""
    url = "https://efa.vrr.de/standard/XML_STOPFINDER_REQUEST"
    params = {
        "language": "de",
        "outputFormat": "JSON",
        "type_sf": "stop",
        "name_sf": city_name,
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    stops = []
    for p in data.get("stopFinder", {}).get("points", []):
        ref = p.get("ref", {})
        if ref.get("place") == city_name:
            stop_id = ref.get("id")
            if stop_id:
                stops.append(stop_id)
    return stops


def fetch_tram_courses(stop_id: str) -> List[Dict]:
    """Return serving lines for the given stop filtered to trams (productId == 1)."""
    url = "https://efa.vrr.de/standard/XML_DM_REQUEST"
    params = {
        "type_dm": "stop",
        "name_dm": stop_id,
        "mode": "direct",
        "useRealtime": "1",
        "outputFormat": "JSON",
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    courses = []
    # Navigate the nested JSON structure to find serving lines.
    points = data.get("stopFinder", {}).get("points", [])
    for point in points:
        for sl in point.get("servingLines", {}).get("servingLine", []):
            product_id = str(sl.get("product", {}).get("id"))
            if product_id != "1":
                continue  # only trams
            diva = sl.get("diva", {})
            courses.append({
                "line_number": diva.get("line"),
                "direction": sl.get("direction"),
                "diva": diva,
            })
    return courses


def fetch_course_progress(diva: Dict) -> Optional[List[Dict]]:
    """Fetch the stop list for a single course using diva parameters."""
    url = "https://efa.vrr.de/standard/XML_DM_REQUEST"
    params = {
        "type_dm": "any",
        "useRealtime": "1",
        "mode": "direct",
        "line": diva.get("line"),
        "dir": diva.get("dir"),
        "branch": diva.get("branch"),
        "outputFormat": "JSON",
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    stops = []
    for s in data.get("journey", {}).get("points", {}).get("point", []):
        name = s.get("nameWO")
        time_str = s.get("ref", {}).get("depTime") or s.get("ref", {}).get("arrTime")
        stops.append({"name": name, "time": time_str})
    return stops if stops else None


def find_current_stop(stops: List[Dict]) -> Optional[Dict]:
    """Return the next or current stop based on the current time."""
    now = datetime.datetime.now().strftime("%H:%M")
    for stop in stops:
        if stop["time"] and stop["time"] >= now:
            return stop
    return stops[-1] if stops else None


def main() -> None:
    city = "Essen"
    try:
        stop_ids = fetch_city_stops(city)
    except requests.RequestException as exc:
        print("Failed to fetch stops:", exc)
        return

    seen: set[Tuple[str, str]] = set()
    courses: List[Dict] = []
    for stop_id in stop_ids:
        try:
            c = fetch_tram_courses(stop_id)
        except requests.RequestException as exc:
            print(f"Failed to fetch lines for stop {stop_id}:", exc)
            continue
        for course in c:
            key = (course["line_number"], course["direction"])
            if key not in seen:
                seen.add(key)
                courses.append(course)

    results = []
    for c in courses:
        try:
            stops = fetch_course_progress(c["diva"])
        except requests.RequestException as exc:
            print(f"Failed to fetch course {c['diva']}:", exc)
            continue
        if not stops:
            continue
        current = find_current_stop(stops)
        results.append({
            "line": c["line_number"],
            "direction": c["direction"],
            "current_stop": current,
        })

    print(json.dumps({"timestamp": datetime.datetime.now().isoformat(), "courses": results}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

from __future__ import annotations

import os
import time
from typing import Any, Dict, List

from flask import Flask, jsonify, render_template, request

# Essen tram lines shown by default
ESSEN_LINES = {"101", "103", "105", "106", "107", "108", "109"}


def is_essen_line(line: str) -> bool:
    """Return True if the line starts with one of the Essen prefixes."""
    return any(line.startswith(l) for l in ESSEN_LINES)

_STOP_NAME_MAP: Dict[str, str] = {}
_HEADSIGN_MAP: Dict[str, str] = {}

def _load_stop_names() -> None:
    """Load stop_id->name mapping from data/stop_names.csv if present."""
    path = os.path.join("data", "stop_names.csv")
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                sid, name = line.rstrip().split(",", 1)
                _STOP_NAME_MAP[sid] = name
    except FileNotFoundError:
        pass

def _load_headsigns() -> None:
    """Load trip_id->headsign mapping from data/headsigns.csv if present."""
    path = os.path.join("data", "headsigns.csv")
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                tid, headsign = line.rstrip().split(",", 1)
                _HEADSIGN_MAP[tid] = headsign
    except FileNotFoundError:
        pass

_load_stop_names()
_load_headsigns()

def get_stop_name(stop_id: str) -> str:
    """Return the stop name for the given ID if known."""
    return _STOP_NAME_MAP.get(stop_id, stop_id)

def get_headsign(trip_id: str) -> str:
    """Return the headsign for the given trip ID if known."""
    return _HEADSIGN_MAP.get(trip_id, "")
import requests
from google.transit import gtfs_realtime_pb2

app = Flask(__name__)

# URL of the public GTFS-Realtime feed
GTFS_URL = os.environ.get("GTFS_URL", "https://realtime.gtfs.de/realtime-free.pb")
# Optional local GTFS-Realtime file path for offline testing
GTFS_FILE = os.environ.get("GTFS_FILE")


# in-memory cache for the decoded feed
_FEED_CACHE: Dict[str, Any] = {"timestamp": 0.0, "vehicles": [], "courses": []}


def load_gtfs_feed() -> List[Dict[str, Any]]:
    """Load and parse the GTFS-Realtime feed with a 10s cache."""
    now = time.time()
    if now - _FEED_CACHE["timestamp"] < 10:
        return _FEED_CACHE["vehicles"]

    try:
        if GTFS_FILE:
            with open(GTFS_FILE, "rb") as f:
                content = f.read()
        else:
            resp = requests.get(GTFS_URL, timeout=10)
            resp.raise_for_status()
            content = resp.content
    except (requests.RequestException, OSError) as exc:
        app.logger.exception("Failed to fetch GTFS feed: %s", exc)
        return _FEED_CACHE["vehicles"]

    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(content)

    vehicles: List[Dict[str, Any]] = []
    courses: List[Dict[str, Any]] = []
    for entity in feed.entity:
        if entity.HasField("vehicle"):
            vehicle = entity.vehicle
            pos = vehicle.position
            trip = vehicle.trip
            line = trip.route_id or trip.trip_id
            if not is_essen_line(line):
                continue
            if pos.HasField("latitude") and pos.HasField("longitude"):
                vehicles.append(
                    {
                        "line": line,
                        "course": vehicle.vehicle.label or trip.trip_id,
                        "lat": pos.latitude,
                        "lon": pos.longitude,
                        "direction": getattr(pos, "bearing", 0.0),
                        "timestamp": vehicle.timestamp or feed.header.timestamp,
                    }
                )
        if entity.HasField("trip_update"):
            tu = entity.trip_update
            trip = tu.trip
            line = trip.route_id or trip.trip_id
            if not is_essen_line(line):
                continue
            vehicle_id = tu.vehicle.label or tu.vehicle.id or ""
            next_stop = None
            ref_time = feed.header.timestamp or int(time.time())
            for s in tu.stop_time_update:
                dep = s.departure.time or s.arrival.time
                if dep >= ref_time:
                    next_stop = s.stop_id
                    break
            if next_stop is None and tu.stop_time_update:
                next_stop = tu.stop_time_update[-1].stop_id
            courses.append(
                {
                    "line": line,
                    "course": trip.trip_id,
                    "vehicle": vehicle_id,
                    "next_stop": next_stop,
                    "headsign": get_headsign(trip.trip_id),
                }
            )

    _FEED_CACHE["timestamp"] = now
    _FEED_CACHE["vehicles"] = vehicles
    _FEED_CACHE["courses"] = courses
    return vehicles


@app.route("/lines")
def get_lines() -> Any:
    """Return a list of available lines from the GTFS feed or file."""
    try:
        with open("data/line.txt", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
    except FileNotFoundError:
        vehicles = load_gtfs_feed()
        lines = sorted({v["line"] for v in vehicles})
        if not lines:
            lines = sorted(ESSEN_LINES)
    lines = [l for l in lines if is_essen_line(l)]
    return jsonify(sorted(lines, key=lambda x: int(x)))


@app.route("/essen_lines")
def get_essen_lines() -> Any:
    """Return the configured Essen tram lines."""
    return jsonify(sorted(ESSEN_LINES, key=lambda x: int(x)))


@app.route("/courses")
def get_courses() -> Any:
    line = request.args.get("line")
    if not line:
        return jsonify([])
    vehicles = load_gtfs_feed()
    courses = sorted({str(v["course"]) for v in vehicles if v["line"] == line})
    return jsonify(courses)


@app.route("/")
def index() -> str:
    line = request.args.get("line", "")
    course = request.args.get("course", "")
    return render_template("index.html", line=line, course=course)


@app.route("/vehicles")
def get_vehicles() -> Any:
    line_filter = request.args.get("line")
    course_filter = request.args.get("course")
    vehicles = load_gtfs_feed()
    if line_filter:
        vehicles = [v for v in vehicles if v["line"] == line_filter]
    if course_filter:
        vehicles = [v for v in vehicles if str(v["course"]) == course_filter]
    return jsonify(vehicles)


@app.route("/missing_courses")
def get_missing_courses() -> Any:
    line_filter = request.args.get("line")
    vehicles = load_gtfs_feed()
    courses = _FEED_CACHE.get("courses", [])
    active = {v["course"] for v in vehicles}
    result = [c.copy() for c in courses if c["course"] not in active]
    if line_filter:
        result = [c for c in result if c["line"] == line_filter]
    for c in result:
        if c.get("next_stop"):
            c["next_stop"] = get_stop_name(str(c["next_stop"]))
    result.sort(key=lambda c: (int(c["line"]), str(c["course"])))
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8021)

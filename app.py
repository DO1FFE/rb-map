from __future__ import annotations

import time
from typing import Any, Dict, List

from flask import Flask, jsonify, render_template, request
import requests
from google.transit import gtfs_realtime_pb2

app = Flask(__name__)

GTFS_URL = "https://realtime.gtfs.de/realtime-free.pb"

# in-memory cache for the decoded feed
_FEED_CACHE: Dict[str, Any] = {"timestamp": 0.0, "vehicles": []}


def load_gtfs_feed() -> List[Dict[str, Any]]:
    """Load and parse the GTFS-Realtime feed with a 10s cache."""
    now = time.time()
    if now - _FEED_CACHE["timestamp"] < 10:
        return _FEED_CACHE["vehicles"]

    try:
        resp = requests.get(GTFS_URL, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as exc:
        app.logger.exception("Failed to fetch GTFS feed: %s", exc)
        return _FEED_CACHE["vehicles"]

    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(resp.content)

    vehicles: List[Dict[str, Any]] = []
    for entity in feed.entity:
        if not entity.HasField("vehicle"):
            continue
        vehicle = entity.vehicle
        pos = vehicle.position
        if not pos.HasField("latitude") or not pos.HasField("longitude"):
            continue
        trip = vehicle.trip
        vehicles.append(
            {
                "line": trip.route_id or trip.trip_id,
                "course": vehicle.vehicle.label or trip.trip_id,
                "lat": pos.latitude,
                "lon": pos.longitude,
                "direction": getattr(pos, "bearing", 0.0),
                "timestamp": vehicle.timestamp or feed.header.timestamp,
            }
        )

    _FEED_CACHE["timestamp"] = now
    _FEED_CACHE["vehicles"] = vehicles
    return vehicles


@app.route("/")
def index() -> str:
    line = request.args.get("line", "")
    return render_template("index.html", line=line)


@app.route("/vehicles")
def get_vehicles() -> Any:
    line_filter = request.args.get("line")
    vehicles = load_gtfs_feed()
    if line_filter:
        vehicles = [v for v in vehicles if v["line"] == line_filter]
    return jsonify(vehicles)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8021)

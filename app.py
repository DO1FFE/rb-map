from flask import Flask, jsonify, render_template, request
import requests

app = Flask(__name__)


def fetch_ruhrbahn_data() -> dict | None:
    """Fetch data from the Ruhrbahn API and return the parsed JSON.

    Returns None if the request fails for any reason.
    """
    url = "https://www.ruhrbahn.de/efaws2/default/XML_VEHICLE_MONITOR_REQUEST"
    try:
        response = requests.get(url, params={"outputFormat": "JSON"}, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        app.logger.exception("Ruhrbahn API request failed: %s", exc)
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/vehicles')
def get_vehicles():
    """Return vehicle positions optionally filtered by line."""
    line_filter = request.args.get("line")
    data = fetch_ruhrbahn_data()
    if data is None:
        return (
            jsonify({"error": "Failed to fetch data from Ruhrbahn API"}),
            502,
        )

    vehicles = []
    for v in data.get("vehicles", []):
        if "position" in v and v.get("number") and v.get("course"):
            if line_filter and v["number"] != line_filter:
                continue
            vehicles.append({
                "lat": v["position"]["lat"],
                "lon": v["position"]["lon"],
                "line": v["number"],
                "course": v["course"],
                "direction": v.get("direction", "?")
            })
    return jsonify(vehicles)


@app.route('/api/lines')
def get_lines():
    """Return a list of available line numbers."""
    data = fetch_ruhrbahn_data()
    if data is None:
        return (
            jsonify({"error": "Failed to fetch data from Ruhrbahn API"}),
            502,
        )
    lines = sorted({v["number"] for v in data.get("vehicles", []) if v.get("number")})
    return jsonify(lines)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8021, debug=True)

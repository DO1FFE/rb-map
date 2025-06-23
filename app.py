from flask import Flask, jsonify, render_template, request
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/vehicles')
def get_vehicles():
    line_filter = request.args.get("line")
    url = "https://www.ruhrbahn.de/efaws2/default/XML_VEHICLE_MONITOR_REQUEST"
    response = requests.get(url, params={"outputFormat": "JSON"})
    response.raise_for_status()
    data = response.json()

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8021, debug=True)

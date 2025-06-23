# Ruhrbahn Vehicle Map

A small Flask application that displays live positions of Ruhrbahn vehicles on a Leaflet map.

## Requirements

- Python 3.11 or newer
- `flask` and `requests` packages

Install dependencies with:

```bash
pip install flask requests
```

## Usage

Run the application:

```bash
python app.py
```

Open `http://localhost:8021` in your browser.

Use the dropdown to filter vehicles by line. The map refreshes automatically every 15 seconds.

## VRR Stop Visit Script

The repository also contains a small helper script `efa_stop_visits.py` that
fetches live departures for a single stop via the public EFA VRR API. Run it
with Python to print the currently monitored lines, courses and stops:

```bash
python efa_stop_visits.py
```

You can change the `stop_id` in the script to query another stop.


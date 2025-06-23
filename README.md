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
with Python to print the currently monitored lines, courses and stops. If the
API request fails, the script prints an error message:

```bash
python efa_stop_visits.py
```

You can change the stop name in the script to query another stop.

## Tram Course Monitor

The script `efa_tram_monitor.py` queries the EFA `XML_DM_REQUEST` interface to
list all active tram lines for a given stop and prints the currently served
stop for each course as JSON. Internet access is required for the requests.

Run it with:

```bash
python efa_tram_monitor.py
```


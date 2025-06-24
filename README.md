# VRR Tram Map

A Flask web application that visualises live tram positions in the VRR region.

## Requirements

- Python 3.11 or newer
- `flask` and `requests` packages

Install dependencies with:

```bash
pip install flask requests protobuf gtfs-realtime-bindings
```

## Usage

Run the application:

```bash
python app.py
```

Open `http://localhost:8021` in your browser.

Only the Essen tram lines (101, 103, 105, 106, 107, 108, 109) are displayed.
Use the dropdown or the URL parameter `?line=107` to focus on a single line.
The map refreshes automatically every 10 seconds.

### Generate line list

The helper script `generate_line_list.py` creates a file `data/line.txt`
containing all lines currently present in the GTFS feed:

```bash
python generate_line_list.py
```

The web application reads this file for the dropdown if it exists.

If a file `data/stop_names.csv` with `stop_id,name` pairs is present, the
application will show the stop name instead of the ID for missing course
information. Otherwise the raw ID is used.
If a file `data/headsigns.csv` with `trip_id,headsign` pairs exists, the
application will show the trip headsign in the list of missing courses.

## VRR Stop Visit Script

The repository also contains a small helper script `efa_stop_visits.py` that
fetches live departures for a single stop via the public EFA VRR API. The
script filters to the Essener tram lines (101, 103, 105, 106, 107, 108, 109)
and prints the stop name instead of the stop ID if available. Run it with
Python to display the currently monitored lines, courses and stops. If the API
request fails, the script prints an error message:

```bash
python efa_stop_visits.py
```

You can change the stop name in the script to query another stop.

## Tram Course Monitor

The script `efa_tram_monitor.py` queries the EFA APIs. In its default
configuration it now collects all tram lines for the city of Essen. For each
unique line and direction the script looks up the current course and determines
the next stop. The output is printed as JSON with a timestamp.

Internet access is required for the requests. Run the monitor with:

```bash
python efa_tram_monitor.py
```


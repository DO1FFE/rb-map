# VRR Tram Map

A Flask web application that visualises live tram positions in the VRR region.

## Requirements

- Python 3.11 or newer
- `flask` and `requests` packages

Install dependencies with:

```bash
pip install flask requests protobuf
```

## Usage

Run the application:

```bash
python app.py
```

Open `http://localhost:8021` in your browser.

Use the dropdown or the URL parameter `?line=107` to filter vehicles by line.
The map refreshes automatically every 15 seconds.

### Generate line list

The helper script `generate_line_list.py` creates a file `data/line.txt`
containing all lines currently present in the GTFS feed:

```bash
python generate_line_list.py
```

The web application reads this file for the dropdown if it exists.

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

The script `efa_tram_monitor.py` queries the EFA APIs. In its default
configuration it now collects all tram lines for the city of Essen. For each
unique line and direction the script looks up the current course and determines
the next stop. The output is printed as JSON with a timestamp.

Internet access is required for the requests. Run the monitor with:

```bash
python efa_tram_monitor.py
```


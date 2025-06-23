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


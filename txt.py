#!/usr/bin/env python3
"""Save the current GTFS-Realtime feed as a text file."""

import json
from app import load_gtfs_feed


def main() -> None:
    vehicles = load_gtfs_feed()
    with open("data/gtfs.txt", "w", encoding="utf-8") as f:
        json.dump(vehicles, f, indent=2, ensure_ascii=False)
    print("Saved GTFS feed to data/gtfs.txt")


if __name__ == "__main__":
    main()

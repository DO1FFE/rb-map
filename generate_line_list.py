#!/usr/bin/env python3
"""Generate a list of tram lines from the GTFS feed."""

from typing import List
from app import load_gtfs_feed


def main() -> None:
    vehicles = load_gtfs_feed()
    lines: List[str] = sorted({v["line"] for v in vehicles})
    with open("data/line.txt", "w", encoding="utf-8") as f:
        for line in lines:
            f.write(f"{line}\n")
    print(f"Wrote {len(lines)} lines to data/line.txt")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common import load_trip, read_json, save_trip, write_json
from export_route_geojson import to_geojson
from validate_route import validate_route


def apply_route_enrichment(trip_dir: Path, route_path: Path) -> dict:
    route = read_json(route_path)
    issues = validate_route(route)
    if issues:
        raise ValueError("enriched route is invalid: " + "; ".join(issues))

    trip = load_trip(trip_dir)
    trip["days"] = route["days"]
    trip["direct_distance_km"] = route.get("direct_distance_km")
    trip["route_distance_km"] = route.get("route_distance_km")
    trip["waypoints"] = route["waypoints"]
    trip["route_enriched"] = True
    trip["route_enrichment_source"] = str(route_path)

    write_json(trip_dir / "route.json", route)
    write_json(trip_dir / "route.geojson", to_geojson(route))
    save_trip(trip_dir, trip)
    return {"status": "route_enrichment_applied", "trip_dir": str(trip_dir), "days": route["days"]}


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply a validated enriched route to trip state.")
    parser.add_argument("--trip-dir", required=True)
    parser.add_argument("--route", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = apply_route_enrichment(Path(args.trip_dir).expanduser(), Path(args.route).expanduser())
    if args.json:
        import json
        import sys

        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(result["status"])


if __name__ == "__main__":
    main()

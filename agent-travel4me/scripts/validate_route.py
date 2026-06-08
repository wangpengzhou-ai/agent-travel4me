#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

from common import load_trip, print_json, read_json


REQUIRED_WAYPOINT_FIELDS = [
    "day",
    "location",
    "country_or_region",
    "coordinates",
    "role",
    "landmarks",
    "landscape_type",
    "local_visual_elements",
    "palette",
    "agent_activity",
    "agent_position",
    "prompt_focus",
    "is_natural_or_semi_natural",
]

PLACEHOLDER_PATTERNS = [
    re.compile(r"route waypoint", re.IGNORECASE),
    re.compile(r"placeholder", re.IGNORECASE),
    re.compile(r"to be resolved", re.IGNORECASE),
    re.compile(r"primary recognizable landmark", re.IGNORECASE),
    re.compile(r"secondary local feature", re.IGNORECASE),
    re.compile(r"locally appropriate", re.IGNORECASE),
]


def _has_placeholder(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return any(pattern.search(value) for pattern in PLACEHOLDER_PATTERNS)
    if isinstance(value, list):
        return any(_has_placeholder(item) for item in value)
    if isinstance(value, dict):
        return any(_has_placeholder(item) for item in value.values())
    return False


def _valid_coordinates(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    lat = value.get("lat")
    lon = value.get("lon")
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        return False
    return -90 <= lat <= 90 and -180 <= lon <= 180


def _is_city_only(waypoint: dict[str, Any]) -> bool:
    if waypoint.get("is_natural_or_semi_natural"):
        return False
    landscape = str(waypoint.get("landscape_type", "")).lower()
    return not any(word in landscape for word in ("river", "water", "mountain", "desert", "forest", "coast", "lake", "harbor", "plain"))


def validate_route(route_or_trip: dict[str, Any]) -> list[str]:
    waypoints = route_or_trip.get("waypoints") or []
    days = route_or_trip.get("days", len(waypoints))
    issues: list[str] = []

    if not waypoints:
        return ["route has no waypoints"]
    if len(waypoints) != days:
        issues.append(f"route has {len(waypoints)} waypoints but days is {days}")

    natural_days = 0
    city_streak = 0
    for index, waypoint in enumerate(waypoints, start=1):
        for field in REQUIRED_WAYPOINT_FIELDS:
            if field not in waypoint:
                issues.append(f"day {index}: missing {field}")

        if _has_placeholder(waypoint.get("location")):
            issues.append(f"day {index}: location is not a real resolved place")
        if _has_placeholder(waypoint.get("country_or_region")):
            issues.append(f"day {index}: country_or_region is unresolved")
        if not _valid_coordinates(waypoint.get("coordinates")):
            issues.append(f"day {index}: coordinates are missing or invalid")

        landmarks = waypoint.get("landmarks")
        if not isinstance(landmarks, list) or not landmarks:
            issues.append(f"day {index}: landmarks are missing")
        elif _has_placeholder(landmarks):
            issues.append(f"day {index}: landmarks contain placeholders")

        for field in ("local_visual_elements", "palette", "agent_activity", "prompt_focus"):
            if _has_placeholder(waypoint.get(field)):
                issues.append(f"day {index}: {field} contains placeholder content")

        if waypoint.get("is_natural_or_semi_natural"):
            natural_days += 1

        if _is_city_only(waypoint):
            city_streak += 1
            if city_streak >= 3:
                issues.append(f"day {index}: three consecutive city-only days")
        else:
            city_streak = 0

    if 15 <= days <= 24 and natural_days < 7:
        issues.append(f"route needs at least 7 natural or semi-natural days; found {natural_days}")
    if 25 <= days <= 30 and natural_days < 10:
        issues.append(f"route needs at least 10 natural or semi-natural days; found {natural_days}")

    return issues


def validate_daily_context(trip: dict[str, Any], day: int) -> list[str]:
    issues = []
    waypoint = trip["waypoints"][day - 1]
    if not waypoint.get("weather"):
        issues.append(f"day {day}: weather is required before live image generation")
    if trip.get("label", {}).get("enabled", True) and not (waypoint.get("label_location") or waypoint.get("location")):
        issues.append(f"day {day}: label location is missing")
    return issues


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trip-dir")
    parser.add_argument("--route")
    parser.add_argument("--require-day-context", type=int)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.trip_dir and not args.route:
        raise SystemExit("pass --trip-dir or --route")

    data = load_trip(Path(args.trip_dir).expanduser()) if args.trip_dir else read_json(Path(args.route))
    issues = validate_route(data)
    if args.require_day_context:
        issues.extend(validate_daily_context(data, args.require_day_context))

    result = {"valid": not issues, "issues": issues}
    if args.json:
        print_json(result)
    else:
        if issues:
            for issue in issues:
                print(issue)
        else:
            print("route valid")
    raise SystemExit(0 if not issues else 2)


if __name__ == "__main__":
    main()

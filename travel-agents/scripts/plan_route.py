#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from common import estimate_days, haversine_km, print_json, write_json


LANDSCAPE_SEQUENCE = [
    {
        "landscape_type": "departure city",
        "role": "departure from the user's current place",
        "local_visual_elements": ["recognizable local skyline", "morning light", "departure object", "street texture"],
        "local_activity": "starting the journey with a small local departure ritual",
        "agent_activity": "pinning a tiny departure ticket to the backpack before departure",
        "human_interaction": "asking a local shopkeeper or station worker for a first route tip",
        "crowd_interaction": "standing among local commuters and departure-day passersby while a station worker gives a small wave",
        "is_natural_or_semi_natural": False,
    },
    {
        "landscape_type": "river or waterfront",
        "role": "first soft transition into open water or river scenery",
        "local_visual_elements": ["water reflections", "riverbank plants", "small boat or bridge", "mist or open sky"],
        "local_activity": "joining a quiet riverside crossing or morning boat routine",
        "agent_activity": "watching a small boat rope being tied beside the water",
        "agent_activity_options": [
            "watching a small boat rope being tied beside the water",
            "holding a tiny crossing token under the bridge shadow",
            "sitting on a low dock while reflections pass",
            "sheltering a postcard pouch from river mist",
            "pointing a tiny camera toward the morning crossing",
        ],
        "human_interaction": "listening to a boat operator or riverside vendor point out the next crossing",
        "crowd_interaction": "waiting with a small riverside queue as boat operators and vendors prepare the crossing",
        "is_natural_or_semi_natural": True,
    },
    {
        "landscape_type": "hills or highland path",
        "role": "entering higher ground",
        "local_visual_elements": ["winding path", "regional plants", "distant ridges", "stone or soil texture"],
        "local_activity": "following a regional walking path and checking handmade trail signs",
        "agent_activity": "sketching the terrain from a low resting spot",
        "agent_activity_options": [
            "sketching the terrain from a low resting spot",
            "tying a tiny scarf against the highland wind",
            "counting painted trail stones near the path edge",
            "brushing dust from a small boot beside regional plants",
            "holding a pressed leaf beside the winding path",
        ],
        "human_interaction": "greeting a local guide, shepherd, or trail caretaker on the path",
        "crowd_interaction": "walking near a loose group of hikers, shepherds, or caretakers while trail markers lead uphill",
        "is_natural_or_semi_natural": True,
    },
    {
        "landscape_type": "local town or old quarter",
        "role": "passing through a place with visible local architecture",
        "local_visual_elements": ["local facade materials", "market awning", "balcony or arcade", "street objects"],
        "local_activity": "pausing at a neighborhood market or street stall",
        "agent_activity": "resting under shade with a small local drink",
        "agent_activity_options": [
            "resting under shade with a small local drink",
            "balancing a tiny paper snack bag under the market awning",
            "peeking from an arcade column toward the street stall",
            "holding a small coin pouch beside local facade tiles",
            "sitting near a balcony shadow with a postcard pouch",
        ],
        "human_interaction": "buying a small local drink or snack from a stall owner",
        "crowd_interaction": "sitting at the edge of a market crowd while stall owners pass snacks under the awning",
        "is_natural_or_semi_natural": False,
    },
    {
        "landscape_type": "mountain, cliff, or dramatic geology",
        "role": "major natural transition",
        "local_visual_elements": ["rock faces", "large sky", "trail markers", "wind-shaped plants"],
        "local_activity": "following regional trail markers through a dramatic natural pass",
        "agent_activity": "standing small on a trail while the landscape dominates",
        "agent_activity_options": [
            "standing small on a trail while the landscape dominates",
            "tightening a tiny backpack strap beside wind-shaped plants",
            "placing one small pebble on a trail cairn",
            "holding a scarf against the cliff wind near a marker",
            "crouching beside a trail marker while rock faces tower above",
        ],
        "human_interaction": "asking a trail caretaker or passing hiker about the safest path ahead",
        "crowd_interaction": "moving with scattered hikers on a lookout path while a ranger keeps the trail edge clear",
        "is_natural_or_semi_natural": True,
    },
    {
        "landscape_type": "plain, desert, grassland, or open country",
        "role": "wide-open crossing",
        "local_visual_elements": ["open horizon", "track or road", "sparse shelter", "weathered local material"],
        "local_activity": "crossing a quiet open-country route and reading regional road markers",
        "agent_activity": "sorting the backpack in a patch of shade",
        "agent_activity_options": [
            "sorting the backpack in a patch of shade",
            "brushing dust from a tiny shoe near the open track",
            "sipping water beside a sparse roadside shelter",
            "tying a scarf while the open horizon fills the frame",
            "holding a small weathered token found by the road edge",
        ],
        "human_interaction": "thanking a local driver or roadside caretaker for directions",
        "crowd_interaction": "pausing near a sparse roadside rest stop where drivers and caretakers gather briefly",
        "can_skip_human_interaction": True,
        "no_human_interaction_reason": "remote open-country crossing where adding a person would feel forced",
        "is_natural_or_semi_natural": True,
    },
    {
        "landscape_type": "harbor, ferry, or strait",
        "role": "water crossing",
        "local_visual_elements": ["ferry rail", "harbor lights", "seabirds or wind", "distant shore"],
        "local_activity": "boarding a local ferry or watching harbor work from the rail",
        "agent_activity": "waiting by a ferry rail with a wind-creased boarding ticket",
        "agent_activity_options": [
            "waiting by a ferry rail with a wind-creased boarding ticket",
            "steadying a postcard pouch against the harbor wind",
            "looking up at a small signal light near the ferry queue",
            "sitting near a coil of rope while harbor lights come on",
            "holding a tiny warm cup beside the ferry rail",
        ],
        "human_interaction": "showing the route card to a ferry attendant or harbor worker",
        "crowd_interaction": "waiting in a ferry queue among local passengers while a harbor worker signals boarding",
        "is_natural_or_semi_natural": True,
    },
    {
        "landscape_type": "arrival city",
        "role": "arrival at the destination",
        "local_visual_elements": ["recognizable arrival landmark", "local pavement", "river or skyline", "arrival light"],
        "local_activity": "marking arrival with a small local postcard or street-side ritual",
        "agent_activity": "holding a final travel postcard",
        "human_interaction": "receiving a final direction or welcome gesture from a local postcard seller",
        "crowd_interaction": "sitting among plaza visitors or cafe regulars while a local seller clears space for the final postcard",
        "is_natural_or_semi_natural": False,
    },
]


VISUAL_WEATHER_SEQUENCE = [
    "clear humid sunrise after light rain, with wet ground reflections and soft haze",
    "cool river mist with damp stone, muted water reflections, and pale morning light",
    "windy highland afternoon, with moving cloud shadows and a scarf tugged by gusts",
    "warm market dusk after a dry day, with lantern glow, dust-soft walls, and shaded air",
    "bright broken sun after passing showers, with wet leaves and sparkling path edges",
    "cold moonlit night or blue-hour air, with protected lantern glow and long quiet shadows",
    "hard salt-air daylight, with glare on water, gull wind, and crisp white highlights",
    "soft overcast evening, with low clouds, saturated colors, and gentle reflected light",
]


def _run_external_route_planner(payload: dict[str, Any]) -> dict[str, Any] | None:
    command = os.environ.get("TRAVEL_AGENTS_ROUTE_COMMAND") or os.environ.get("TRAVEL4ME_ROUTE_COMMAND")
    if not command:
        return None
    result = subprocess.run(command, input=json.dumps(payload), text=True, shell=True, capture_output=True, timeout=120, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"TRAVEL_AGENTS_ROUTE_COMMAND failed: {result.stderr or result.stdout}")
    return json.loads(result.stdout)


def _interpolate(start: dict[str, float], end: dict[str, float], t: float) -> dict[str, float]:
    return {
        "lat": round(start["lat"] + (end["lat"] - start["lat"]) * t, 4),
        "lon": round(start["lon"] + (end["lon"] - start["lon"]) * t, 4),
    }


def _day_count(
    origin_coords: dict[str, float] | None,
    destination_coords: dict[str, float] | None,
    target_days: int | None,
) -> tuple[int, int | None, str]:
    distance = None
    if origin_coords and destination_coords:
        distance = round(haversine_km((origin_coords["lat"], origin_coords["lon"]), (destination_coords["lat"], destination_coords["lon"])))
    if target_days:
        return max(3, min(30, target_days)), distance, "user_target"
    if distance is not None:
        return estimate_days(distance), distance, "distance_estimate"
    return 12, None, "fallback_no_coordinates"


def _landscape_for(day_index: int, total_days: int) -> dict[str, Any]:
    if day_index == 0:
        return LANDSCAPE_SEQUENCE[0]
    if day_index == total_days - 1:
        return LANDSCAPE_SEQUENCE[-1]
    inner = LANDSCAPE_SEQUENCE[1:-1]
    return inner[(day_index - 1) % len(inner)]


def _agent_activity_for(template: dict[str, Any], day_index: int, total_days: int) -> str:
    options = template.get("agent_activity_options")
    if not options:
        return template["agent_activity"]
    if day_index == 0 or day_index == total_days - 1:
        return str(options[0])
    inner_len = max(1, len(LANDSCAPE_SEQUENCE) - 2)
    cycle = (day_index - 1) // inner_len
    return str(options[cycle % len(options)])


def _solo_scene_days(total_days: int) -> set[int]:
    if total_days < 4:
        return set()
    return {index for index in range(1, total_days - 1) if index % 4 == 2}


def _crowd_scene_days(total_days: int) -> set[int]:
    if total_days < 3:
        return set()
    return {index for index in range(total_days) if index in (0, total_days - 1) or index % 4 == 0}


def _social_mode_for(day_index: int, total_days: int) -> str:
    if day_index in _solo_scene_days(total_days):
        return "solo"
    if day_index in _crowd_scene_days(total_days):
        return "crowd_context"
    return "small_interaction"


def _human_interaction_for(template: dict[str, Any], social_mode: str) -> str:
    if social_mode == "solo":
        return "none"
    if social_mode == "crowd_context":
        return str(template.get("crowd_interaction") or template["human_interaction"])
    return template["human_interaction"]


def _no_human_interaction_reason_for(template: dict[str, Any], social_mode: str) -> str | None:
    if social_mode != "solo":
        return None
    return str(
        template.get("no_human_interaction_reason")
        or f"quiet {template['landscape_type']} pause where a solitary travel moment gives the route more visual variety"
    )


def _visual_weather_for(day_index: int) -> str:
    return VISUAL_WEATHER_SEQUENCE[day_index % len(VISUAL_WEATHER_SEQUENCE)]


def _agent_position_for(template: dict[str, Any], social_mode: str) -> str:
    if social_mode == "solo":
        return f"small off-center traveler in a quiet mid-ground edge of the {template['landscape_type']} scene"
    if social_mode == "crowd_context":
        return "small off-center traveler visible at the edge of a broader local crowd, never isolated as a mascot"
    return "small off-center traveler naturally participating in the local environment"


def _make_placeholder_landmarks(location: str, landscape_type: str) -> list[str]:
    return [
        f"primary recognizable landmark for {location}",
        f"secondary local feature fitting {landscape_type}",
    ]


def plan_route(
    origin: str,
    destination: str,
    origin_coords: dict[str, float] | None = None,
    destination_coords: dict[str, float] | None = None,
    target_days: int | None = None,
) -> dict[str, Any]:
    external_payload = {
        "origin": origin,
        "destination": destination,
        "origin_coords": origin_coords,
        "destination_coords": destination_coords,
        "target_days": target_days,
        "requirements": {
            "max_days": 30,
            "day_count_policy": "25-30 days for cross-continent, polar, or over-8000km routes unless user_target is explicit",
            "include_coordinates": True,
            "include_landmarks": True,
            "avoid_three_city_days": True,
            "include_natural_or_semi_natural_days": True,
            "include_local_activity": True,
            "include_human_interaction": True,
            "local_activity_must_be_place_specific": True,
            "human_interaction_must_be_place_specific": True,
            "vary_scene_social_mode": ["solo", "small_interaction", "crowd_context"],
            "include_at_least_one_solo_scene_when_days_gte_4": True,
            "include_at_least_one_crowd_scene_when_days_gte_4": True,
            "avoid_one_on_one_human_interaction_every_day": True,
            "max_no_human_interaction_ratio": 0.35,
            "no_human_interaction_requires_reason": True,
            "include_visual_weather_or_atmosphere": True,
            "visual_weather_is_not_live_weather": True,
            "write_activity_and_interaction_during_route_planning": True,
        },
    }
    external = _run_external_route_planner(external_payload)
    if external:
        return external

    days, direct_distance, day_count_source = _day_count(origin_coords, destination_coords, target_days)
    start = origin_coords or {"lat": 0.0, "lon": 0.0}
    end = destination_coords or {"lat": 0.0, "lon": 0.0}
    has_real_coords = origin_coords is not None and destination_coords is not None

    waypoints = []
    for idx in range(days):
        t = idx / max(1, days - 1)
        template = _landscape_for(idx, days)
        if idx == 0:
            location = origin
        elif idx == days - 1:
            location = destination
        else:
            location = f"Route waypoint {idx + 1}"
        coords = _interpolate(start, end, t) if has_real_coords else {"lat": None, "lon": None}
        landscape_type = template["landscape_type"]
        social_mode = _social_mode_for(idx, days)
        waypoints.append(
            {
                "day": idx + 1,
                "location": location,
                "country_or_region": "to be resolved",
                "coordinates": coords,
                "role": template["role"],
                "landmarks": _make_placeholder_landmarks(location, landscape_type),
                "landscape_type": landscape_type,
                "local_visual_elements": template["local_visual_elements"],
                "palette": ["locally appropriate colors", "route-specific light", "style-consistent accents"],
                "local_activity": template["local_activity"],
                "agent_activity": _agent_activity_for(template, idx, days),
                "scene_social_mode": social_mode,
                "human_interaction": _human_interaction_for(template, social_mode),
                "no_human_interaction_reason": _no_human_interaction_reason_for(template, social_mode),
                "visual_weather": _visual_weather_for(idx),
                "agent_position": _agent_position_for(template, social_mode),
                "prompt_focus": f"{landscape_type} with recognizable local identity",
                "is_natural_or_semi_natural": template["is_natural_or_semi_natural"],
                "needs_enrichment": True,
            }
        )

    route_distance = None
    if has_real_coords:
        route_distance = round(
            sum(
                haversine_km(
                    (a["coordinates"]["lat"], a["coordinates"]["lon"]),
                    (b["coordinates"]["lat"], b["coordinates"]["lon"]),
                )
                for a, b in zip(waypoints, waypoints[1:])
            )
        )

    return {
        "origin": origin,
        "destination": destination,
        "days": days,
        "direct_distance_km": direct_distance,
        "route_distance_km": route_distance,
        "day_count_source": day_count_source,
        "requested_target_days": target_days,
        "human_interaction_policy": {
            "default": "vary social density across solo moments, small local interactions, and broader crowd scenes",
            "max_no_human_interaction_ratio": 0.35,
            "exception_rule": "solo scenes are allowed when they make the route visually less repetitive and include a reason",
        },
        "needs_enrichment": True,
        "enrichment_note": "No external route/geocoding command was configured. A coding agent should enrich route waypoints with real city/region names, landmarks, local visual elements, coordinates, varied scene_social_mode values, visual weather or atmosphere, and place-specific local activities and human interactions before live generation.",
        "waypoints": waypoints,
    }


def _coords(prefix: str, args: argparse.Namespace) -> dict[str, float] | None:
    lat = getattr(args, f"{prefix}_lat")
    lon = getattr(args, f"{prefix}_lon")
    if lat is None or lon is None:
        return None
    return {"lat": lat, "lon": lon}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--origin", required=True)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--origin-lat", type=float)
    parser.add_argument("--origin-lon", type=float)
    parser.add_argument("--destination-lat", type=float)
    parser.add_argument("--destination-lon", type=float)
    parser.add_argument("--target-days", type=int)
    parser.add_argument("--out")
    args = parser.parse_args()

    route = plan_route(
        args.origin,
        args.destination,
        _coords("origin", args),
        _coords("destination", args),
        args.target_days,
    )
    if args.out:
        write_json(Path(args.out), route)
    else:
        print_json(route)


if __name__ == "__main__":
    main()

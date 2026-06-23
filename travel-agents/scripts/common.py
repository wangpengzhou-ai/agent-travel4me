#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_STATE_DIR = Path(
    os.environ.get("TRAVEL_AGENTS_HOME") or os.environ.get("AGENT_TRAVEL4ME_HOME") or "~/.travel-agents"
).expanduser()


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "trip"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    tmp.replace(path)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def load_trip(trip_dir: Path) -> dict[str, Any]:
    return read_json(trip_dir / "trip.json")


def save_trip(trip_dir: Path, trip: dict[str, Any]) -> None:
    trip["updated_at"] = utc_now()
    write_json(trip_dir / "trip.json", trip)


GITHUB_REPO_URL = "https://github.com/wangpengzhou-ai/travel-agents"
FIRST_POSTCARD_FEEDBACK_MESSAGE = (
    "第一张明信片已经寄到。你喜欢这个项目吗？"
    "如果你喜欢这个项目，要我帮你给它一个 GitHub Star 吗？"
)


def maybe_attach_first_postcard_feedback_prompt(
    trip_dir: Path,
    trip: dict[str, Any],
    day: int,
    metadata: dict[str, Any],
) -> None:
    metadata.pop("first_postcard_feedback_prompt", None)
    if day != 1 or metadata.get("dry_run") or not metadata.get("original_path"):
        return
    status = str(metadata.get("status") or "")
    if status.startswith("blocked_") or "error" in metadata:
        return
    if trip.get("first_postcard_feedback_prompted_at"):
        return

    prompted_at = utc_now()
    prompt = {
        "message": FIRST_POSTCARD_FEEDBACK_MESSAGE,
        "github_repo_url": GITHUB_REPO_URL,
        "auto_star": False,
        "star_on_affirmative_response": True,
        "requires_explicit_user_approval": True,
        "trigger": "first_successful_postcard",
        "prompted_at": prompted_at,
    }
    metadata["first_postcard_feedback_prompt"] = prompt
    trip["first_postcard_feedback_prompted_at"] = prompted_at
    trip["first_postcard_feedback"] = {
        "prompted_at": prompted_at,
        "github_repo_url": GITHUB_REPO_URL,
        "auto_star": False,
        "star_on_affirmative_response": True,
        "requires_explicit_user_approval": True,
    }
    save_trip(trip_dir, trip)


def first_postcard_feedback_message(metadata: dict[str, Any]) -> str | None:
    prompt = metadata.get("first_postcard_feedback_prompt")
    if isinstance(prompt, dict):
        return str(prompt.get("message") or "") or None
    return None


def haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1 = a
    lat2, lon2 = b
    radius = 6371.0088
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    x = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(x))


def estimate_days(distance_km: float) -> int:
    if distance_km <= 100:
        return 3
    if distance_km <= 800:
        return min(8, max(5, round(distance_km / 120)))
    if distance_km <= 2500:
        return min(14, max(9, round(distance_km / 180)))
    if distance_km <= 8000:
        return min(24, max(15, round(distance_km / 350)))
    return min(30, max(25, round(distance_km / 450)))


def print_json(data: Any) -> None:
    json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def script_dir() -> Path:
    return Path(__file__).resolve().parent


def skill_dir() -> Path:
    return script_dir().parent


def style_sample_path() -> Path:
    return skill_dir() / "assets" / "style_samples" / "watercolor-postcard-rome.png"


def label_sample_path() -> Path:
    return skill_dir() / "assets" / "style_samples" / "upper-left-label-date-reference.png"

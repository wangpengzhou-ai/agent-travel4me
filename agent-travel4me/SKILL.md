---
name: agent-travel4me
description: Plan and run an "Agent travels for me" journey for a user: infer or ask origin and destination, create a consistent small Agent traveler, plan a route with landmarks/nature/local visual elements, generate daily route scenes, prompts, and optional images, optionally resize an image for wallpaper use, optionally set the desktop wallpaper, and export route data for visualization.
---

# agent-travel4me

Use this skill when the user wants an AI Agent to "travel for me" and maintain a multi-day journey along a route.

This is a portable coding-agent skill. It does not assume a client UI. Work through local files and scripts.

## Overview

`agent-travel4me` turns a user's travel wish into a local, multi-day Agent journey. The agent acts as a small recurring traveler moving from an origin to a destination. For each day, the workflow chooses a waypoint, builds a scene prompt with recognizable local details, can optionally generate an image, and advances the trip state.

The skill is for "Agent travels for me" narrative production, not travel booking or real itinerary advice. The route should be visually coherent and geographically plausible. The main deliverable is durable journey state, route data, daily scene prompts, and optional visual artifacts. Desktop wallpaper is one supported presentation option, not the purpose of the skill.

## Inputs To Collect

- Destination: ask first.
- Origin: infer only if local Memory or context makes it likely, then confirm.
- Agent identity: ask how the user imagines the agent as a small travel companion.
- Visual style: use a preset if the user chooses one; otherwise pick a suitable default and mention it.
- Day count: estimate automatically from distance, cap at 30 days, and let the user shorten it.

## Expected Outputs

A complete run should create or update a trip directory under `~/.agent-travel4me/trips/<trip_id>/` with:

- `trip.json`: durable trip state, current day, style, character identity, and waypoints.
- `route.json`: planned route data.
- `route.geojson`: map-friendly route output for visualization.
- `character_reference_prompt.txt`: prompt for the recurring Agent traveler.
- `character_reference.png`, when image generation is available and succeeds.
- `day_###/prompt.txt`: scene/image prompt for that day's waypoint.
- `day_###/metadata.json`: generation status, paths, provider metadata, and errors if any.
- `day_###/original.png`, when image generation is available and succeeds.
- `day_###/wallpaper.png`: desktop-sized optional presentation output after resize/crop, when image generation is available and succeeds.

If image generation is unavailable, the skill should still produce route data and prompts, then clearly state which local provider, API key, or native image tool is missing.

## Operating Rules

1. Start with environment detection:
   ```bash
   python scripts/detect_environment.py
   ```
2. Minimize questions. Ask destination first. Infer origin from Memory only as a guess and confirm it.
3. Ask for the user's Agent identity in a personal voice:
   - "在你眼中，我是什么形象？我可以先试着成为……"
   - Offer 2-4 varied candidates based on available Memory and context.
4. Generate or prompt for a character reference before daily scene images. Ask the user to confirm it.
5. Estimate journey length automatically, capped at 30 days. Confirm the estimate:
   - "我算了一下，从 {origin} 到 {destination}，我大概需要 {days} 天能抵达。你想让我更快一点吗？如果想，告诉我你希望几天内到，我会换更快的交通工具。"
6. Agent must remain a small recurring traveler, not the main subject. It should interact with the environment sometimes, and quietly watch scenery sometimes.
7. Do not put the Agent in the center. Do not repeat lower-left/lower-right standing poses.
8. Do not ask the user to paste API keys. Ask them to set local environment variables.
9. Do not automatically set wallpaper until the user explicitly allows it.

## Provider Priority

Choose the first available generation path:

1. Native agent image generation tool, if the current agent exposes one.
2. `gpt-image-2` through `OPENAI_API_KEY`.
3. Nano Banana 2 / Gemini image model through `GOOGLE_API_KEY` or `GEMINI_API_KEY`.
4. Seedream latest available model through `SEEDREAM_API_KEY` or a configured command hook.

If none are available, still create route data and prompts. Tell the user which key or capability is missing.

## Core Workflow

## Style Presets And Samples

Read `references/style_presets.md` when the user asks to choose or compare visual styles. Bundled samples live in `assets/style_samples/`:

- `high_quality_3d_animation`: `assets/style_samples/3d-animation-new-york.png`
- `anime_travel`: `assets/style_samples/anime-travel-guanajuato.png`
- `watercolor_postcard`: `assets/style_samples/watercolor-postcard-rome.png`
- `cinematic_landscape`: `assets/style_samples/cinematic-landscape-sydney.png`

### 1. Detect

```bash
python scripts/detect_environment.py --json
```

Use the result to decide whether image generation, screen detection, automation, and wallpaper setting are available.

### 2. Initialize Trip

After the user confirms origin, destination, character, and day count:

```bash
python scripts/init_trip.py \
  --origin "<origin city or region>" \
  --destination "<destination city or region>" \
  --character "<confirmed Agent appearance>" \
  --style watercolor_postcard
```

This writes `trip.json`, `route.geojson`, prompts, and state under `~/.agent-travel4me/trips/<trip_id>/` by default.

If coordinates are known or supplied by a geocoder, pass them with `--origin-lat`, `--origin-lon`, `--destination-lat`, and `--destination-lon`. If not, the route is marked `needs_enrichment`; the coding agent must enrich waypoints with real places, landmarks, local visual elements, and coordinates before live image generation.

### 3. Generate Character Reference

Dry run:

```bash
python scripts/generate_character_reference.py --trip-dir <trip_dir> --dry-run
```

Live run, if API/tooling is available:

```bash
python scripts/generate_character_reference.py --trip-dir <trip_dir>
```

Ask user to confirm the resulting reference before generating daily scene images.

### 4. Generate Daily Scene Image

Dry run:

```bash
python scripts/daily_run.py --trip-dir <trip_dir> --dry-run
```

Live run:

```bash
python scripts/daily_run.py --trip-dir <trip_dir>
```

To set wallpaper after generation:

```bash
python scripts/daily_run.py --trip-dir <trip_dir> --set-wallpaper
```

Only use `--set-wallpaper` after user approval.

## Route Quality

Each waypoint must include:

- location name
- country or region
- coordinates
- role in the journey
- landmarks
- landscape type
- local visual elements
- palette
- agent activity
- prompt focus

For 15-24 day routes, at least 7 days should be natural or semi-natural. For 25-30 day routes, at least 10 days should be natural or semi-natural. Avoid three consecutive city-only days.

## Prompt Quality

Generated prompts must include:

- recognizable landmarks
- varied landscapes
- local visual elements
- consistent Agent identity
- varied, context-aware Agent interaction
- wide-image layout with negative space, so the image can work as wallpaper if the user wants that output
- negative constraints: no text, no logos, no watermark, no centered Agent, no close-up mascot shot

Read `references/prompt_contract.md` for the exact prompt contract.

## References

- `references/environment_detection.md`
- `references/route_planning.md`
- `references/prompt_contract.md`
- `references/style_presets.md`
- `references/wallpaper_platforms.md`

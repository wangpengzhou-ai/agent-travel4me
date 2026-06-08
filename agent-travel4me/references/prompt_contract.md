# Prompt Contract

Prompt generation serves three goals:

1. Make the place recognizable.
2. Keep the same Agent identity.
3. Keep the Agent small, varied, and naturally participating in the environment.
4. Keep the upper-left place/date label consistent across days.

## Wallpaper Prompt Fields

Include these fields in order:

1. `style_bible`
2. `location_context`
3. `landmarks`
4. `landscape_type`
5. `local_visual_elements`
6. `weather_context`
7. `agent_identity`
8. `agent_activity`
9. `agent_composition_rule`
10. `upper_left_travel_label`
11. `wallpaper_layout`
12. `negative_constraints`

## Upper-left Travel Label

If `trip.label.enabled` is true, the image generation model should draw the place/date label inside the artwork. Local post-processing overlays are outside this workflow.

Rules:

- Put exactly one label in the upper-left safe area.
- Use exact text from `label_text`, with no paraphrase.
- Keep the same margin, scale, ink color, and lettering style across days.
- Make the label feel painted or printed into the postcard artwork.
- Keep all other areas free of readable text.
- Prefer short label text such as `BACUIT BAY / JUN 08 2026`; use `label_location` when the route location name is too long.

## Weather Context

For live daily generation, get or infer the day's local weather before building the prompt. Weather should affect sky, light, water or ground texture, clothing details, and mood while staying integrated into the scene.

## Character Identity Lock

Daily prompts must include the durable character description, fixed visual anchors, and consistency rules from `trip.character` or `character.json`. The model should vary only the Agent's tiny activity and placement, not the Agent's design.

Rules:

- Keep the same silhouette, body proportions, signature colors, accessories, material feel, and character type across days.
- Avoid age shifts, costume swaps, redesigns, and species/type changes.
- If `character_reference.png` exists and the provider or host agent supports image references, use it for every daily image.
- If the host agent lacks image-reference support, make the text identity lock explicit in the prompt.

## Agent Activity

Vary the Agent's placement instead of defaulting to the lower-left or lower-right corner. Choose one context-aware interaction from the day's local visual elements.

Examples of interaction sources:

- roof eave
- bridge
- station
- riverbank
- tea stall
- market
- boat
- mountain path
- bench
- balcony
- steps
- hot air balloon
- ferry
- awning
- map
- laptop
- camera
- local food

Rules:

- Use at most one small activity per image.
- Keep activities varied across eating, transport, resting, observing, and route-checking scenes.
- Allow about 30-40% of days to be quiet scenery-watching days.
- The Agent occupies less than 6% of image area.
- The Agent is off-center.
- The destination landscape and landmarks are the main subject.

Use this exact negative constraint block in generated prompts:

```text
Avoid: centered agent, close-up agent, mascot poster, repeated lower-corner standing pose, extra animals, readable text outside the exact upper-left travel label, logos, watermarks, wrong landmarks, generic tourist collage.
```

## Skeleton

```text
Create a 16:9 travel wallpaper in {style_name}.
Scene: Day {day}/{total}, {location}, {country_or_region}.
Main visual subject: {landscape_type} with {landmarks}.
Local visual elements: {local_visual_elements}.
Weather: {weather_context}. Let the weather shape the sky, light, water or ground texture, clothing details, and mood.
Journey continuity: the same tiny agent traveler is passing through this place on the way from {origin} to {destination}.
Agent: {character_identity}. The agent is small, off-center, naturally participating in the local environment, occupying less than 6% of the image.
Agent activity: {context-aware interaction}.
Upper-left travel label: draw exactly one small hand-lettered postcard label in the upper-left safe area. Exact text: "{label_text}". Keep the same label position, margin, scale, ink color, and lettering style across every day. Make it feel painted or printed into the artwork.
Composition: wide landscape wallpaper, destination and environment are the main subject, clear negative space for desktop icons.
Avoid: centered agent, close-up agent, mascot poster, repeated lower-corner standing pose, extra animals, readable text outside the exact upper-left travel label, logos, watermarks, wrong landmarks, generic tourist collage.
```

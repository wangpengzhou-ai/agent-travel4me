# Environment Detection

`detect_environment.py` reports a best-effort capability snapshot.

Important distinction:

- Host coding agents may expose native tools outside local Python's visibility, such as image generation, weather/search, reminders, or browser automation.
- CLI coding agent in the user's local logged-in desktop session can often detect screen size and set wallpaper.
- CLI coding agent over SSH, CI, sandbox, or headless runner usually has limited wallpaper and screen-detection access.
- GUI agent access still depends on system permissions.

Detection outputs:

- `native_image_tool_hint`: whether the surrounding agent likely has direct image generation. The value can also be supplied by environment variable `TRAVEL4ME_NATIVE_IMAGE_TOOL=1`.
- `image_provider`: highest-priority API provider available by environment variables.
- `desktop_session`: whether DISPLAY/Wayland/macOS Aqua/Windows session hints exist.
- `screen`: result of best-effort screen detection.
- `wallpaper`: adapter availability.
- `automation`: available scheduler hints.

Image provider priority:

1. `gpt-image-2` with `OPENAI_API_KEY`.
2. Nano Banana 2 / Gemini image model with `GOOGLE_API_KEY` or `GEMINI_API_KEY`.
3. Seedream latest configured model with `SEEDREAM_API_KEY` or `TRAVEL4ME_IMAGE_COMMAND`.

When a native host image tool can satisfy the task, use it before requesting local API-provider setup. For exact-size image generation, check whether that tool exposes a size parameter; if not, generate at a close aspect ratio and resize locally. After host-native generation, use `scripts/import_generated_image.py` to register the result in local trip state.

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import platform
import re
import subprocess
from pathlib import Path


def launchd_plist(name: str, trip_dir: Path, hour: int, minute: int, skill_dir: Path) -> str:
    daily_run = skill_dir / "scripts" / "daily_run.py"
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>{name}</string>
  <key>ProgramArguments</key>
  <array>
    <string>{os.environ.get("PYTHON", "python3")}</string>
    <string>{daily_run}</string>
    <string>--trip-dir</string>
    <string>{trip_dir}</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key><integer>{hour}</integer>
    <key>Minute</key><integer>{minute}</integer>
  </dict>
  <key>StandardOutPath</key><string>{trip_dir}/daily_run.out.log</string>
  <key>StandardErrorPath</key><string>{trip_dir}/daily_run.err.log</string>
</dict>
</plist>
    '''


def _default_name(trip_dir: Path) -> str:
    suffix = re.sub(r"[^a-zA-Z0-9_.-]+", "-", trip_dir.name).strip("-") or "trip"
    return f"com.agent-travel4me.daily.{suffix}"


def _install_launchd(name: str, content: str) -> Path:
    launch_agents = Path.home() / "Library" / "LaunchAgents"
    launch_agents.mkdir(parents=True, exist_ok=True)
    plist_path = launch_agents / f"{name}.plist"
    plist_path.write_text(content, encoding="utf-8")
    subprocess.run(["launchctl", "load", "-w", str(plist_path)], check=False, capture_output=True, text=True)
    return plist_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or print a daily scheduler setup artifact.")
    parser.add_argument("--trip-dir", required=True)
    parser.add_argument("--hour", type=int, default=9)
    parser.add_argument("--minute", type=int, default=0)
    parser.add_argument("--name")
    parser.add_argument("--install", action="store_true", help="Install the scheduler where this script supports it.")
    parser.add_argument("--out")
    args = parser.parse_args()

    system = platform.system()
    skill_dir = Path(__file__).resolve().parent.parent
    trip_dir = Path(args.trip_dir).expanduser().resolve()
    label = args.name or _default_name(trip_dir)
    if system == "Darwin":
        content = launchd_plist(label, trip_dir, args.hour, args.minute, skill_dir)
        if args.install:
            print(_install_launchd(label, content))
        elif args.out:
            Path(args.out).write_text(content, encoding="utf-8")
            print(args.out)
        else:
            print(content)
    elif system == "Linux":
        daily_run = skill_dir / "scripts" / "daily_run.py"
        print(f"{args.minute} {args.hour} * * * {os.environ.get('PYTHON', 'python3')} {daily_run} --trip-dir {trip_dir}")
    elif system == "Windows":
        daily_run = skill_dir / "scripts" / "daily_run.py"
        print(f'schtasks /Create /SC DAILY /TN agent-travel4me /TR "python {daily_run} --trip-dir {trip_dir}" /ST {args.hour:02d}:{args.minute:02d}')
    else:
        raise SystemExit(f"unsupported platform {system}")


if __name__ == "__main__":
    main()

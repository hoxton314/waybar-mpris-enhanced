#!/usr/bin/env python3
"""
Enhanced Custom Waybar MPRIS module
Outputs structured data for use with Waybar's group module
"""

import argparse
import hashlib
import json
import os
import subprocess
import tempfile

PLAYER_ICONS = {
    "default": "",
    "spotify": "",
    "chromium": "",
    "edge": "",
    "vlc": "󰕼",
    "mpv": "",
    "soundcloud": "",
    "optional": ""
}

STATUS_ICONS = {
    "paused": "",
    "playing": "",
    "stopped": "",
    "default": ""
}

def run_playerctl(args):
    """Run playerctl command and return output"""
    try:
        result = subprocess.run(
            ["playerctl"] + args,
            capture_output=True,
            text=True,
            timeout=2
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None

def get_player_info():
    """Get current player information"""
    player = run_playerctl(["metadata", "--format", "{{playerName}}"])
    if not player:
        return None

    title = run_playerctl(["metadata", "--format", "{{title}}"]) or "Unknown"
    artist = run_playerctl(["metadata", "--format", "{{artist}}"]) or "Unknown"
    status = run_playerctl(["status"]) or "Stopped"

    return {
        "player": player.lower(),
        "title": title,
        "artist": artist,
        "status": status
    }

def truncate_text(text, max_len):
    """Truncate text to max length with ellipsis"""
    if len(text) <= max_len:
        return text
    return text[:max_len - 1] + "…"


def get_scroll_state_file(text):
    """Get the path to the scroll state file for the given text"""
    text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
    return os.path.join(tempfile.gettempdir(), f"waybar-mpris-scroll-{text_hash}")


def get_scrolling_text(text, max_len, scroll_speed=1):
    """
    Get scrolling text with state persistence.
    Returns a window of text that shifts on each call.
    """
    if len(text) <= max_len:
        return text

    # Add separator for continuous scrolling effect
    padded_text = text + "   ·   "
    total_len = len(padded_text)

    state_file = get_scroll_state_file(text)

    # Read current position
    try:
        with open(state_file) as f:
            position = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        position = 0

    # Calculate the visible window
    visible_text = ""
    for i in range(max_len):
        idx = (position + i) % total_len
        visible_text += padded_text[idx]

    # Update position for next call
    new_position = (position + scroll_speed) % total_len
    try:
        with open(state_file, 'w') as f:
            f.write(str(new_position))
    except OSError:
        pass

    return visible_text


def main():
    parser = argparse.ArgumentParser(description="Enhanced Waybar MPRIS module")
    parser.add_argument("component", nargs="?", default="info",
                        choices=["prev", "play", "next", "info", "endash", "player-icon"],
                        help="Component to display")
    parser.add_argument("--scroll", action="store_true",
                        help="Enable scrolling text for long titles (info component only)")
    parser.add_argument("--max-length", type=int, default=25,
                        help="Maximum text length before truncating/scrolling (default: 25)")
    parser.add_argument("--scroll-speed", type=int, default=1,
                        help="Number of characters to scroll per update (default: 1)")

    args = parser.parse_args()
    component = args.component

    info = get_player_info()

    if not info and component == "info":
        output = {
            "text": "",
            "tooltip": "No media playing",
            "class": "stopped"
        }
        print(json.dumps(output))
        return

    if not info:
        # Don't show buttons if no player active
        print(json.dumps({"text": "", "class": "custom-enhanced-mpris-hidden"}))
        return

    if component == "endash":
        output = {
            "text": "-",
            "class": "endash"
        }
    elif component == "player-icon":
        player_icon = PLAYER_ICONS.get(info["player"], PLAYER_ICONS["default"])

        output = {
            "text": f"{player_icon}",
            "class": "media-info"
        }
    elif component == "prev":
        output = {
            "text": "󰒮",
            # "tooltip": "Previous track",
            "class": "media-button prev"
        }
    elif component == "play":
        # Show Pause icon when playing, Play icon when paused
        status_icon = "" if info["status"] == "Playing" else ""
        tooltip = "Pause" if info["status"] == "Playing" else "Play"
        output = {
            "text": status_icon,
            # "tooltip": tooltip,
            "class": f"media-button play {info['status'].lower()}"
        }
    elif component == "next":
        output = {
            "text": "󰒭",
            # "tooltip": "Next track",
            "class": "media-button next"
        }
    else:  # info
        player_icon = PLAYER_ICONS.get(info["player"], PLAYER_ICONS["default"])

        if args.scroll:
            title = get_scrolling_text(info["title"], args.max_length, args.scroll_speed)
        else:
            title = truncate_text(info["title"], args.max_length)

        # if info["status"] == "Paused":
        #     text = f"{player_icon} <i>{title}</i>"
        # else:
        #     text = f"{player_icon} {title}"

        text = f"{player_icon}  {title}"

        tooltip = f"{player_icon} {info['player'].title()}: {info['artist']} - {info['title']}"

        output = {
            "text": text,
            "tooltip": tooltip,
            "class": f"media-info {info['status'].lower()}"
        }

    print(json.dumps(output))

if __name__ == "__main__":
    main()

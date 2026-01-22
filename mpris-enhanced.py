#!/usr/bin/env python3
"""
Enhanced Custom Waybar MPRIS module
Outputs structured data for use with Waybar's group module
"""

import json
import subprocess
import sys

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

def main():
    # Check which component to display (prev, play, next, or info)
    component = sys.argv[1] if len(sys.argv) > 1 else "info"
    
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
        title = truncate_text(info["title"], 25)
        
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
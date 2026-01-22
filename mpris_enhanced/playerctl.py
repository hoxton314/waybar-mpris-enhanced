"""Playerctl interaction for MPRIS module."""

__all__ = ["PlayerInfo", "run_playerctl", "get_player_info"]

import subprocess
from dataclasses import dataclass


@dataclass
class PlayerInfo:
    """Information about the current media player."""

    player: str
    title: str
    artist: str
    status: str


def run_playerctl(args: list[str]) -> str | None:
    """Run playerctl command and return output."""
    try:
        result = subprocess.run(
            ["playerctl"] + args,
            capture_output=True,
            text=True,
            timeout=2,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def get_player_info() -> PlayerInfo | None:
    """Get current player information."""
    player = run_playerctl(["metadata", "--format", "{{playerName}}"])
    if not player:
        return None

    title = run_playerctl(["metadata", "--format", "{{title}}"]) or "Unknown"
    artist = run_playerctl(["metadata", "--format", "{{artist}}"]) or "Unknown"
    status = run_playerctl(["status"]) or "Stopped"

    return PlayerInfo(
        player=player.lower(),
        title=title,
        artist=artist,
        status=status.lower(),
    )

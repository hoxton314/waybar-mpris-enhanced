"""Playerctl interaction for MPRIS module.

This module handles all communication with playerctl to retrieve
information about active MPRIS media players.
"""

__all__ = ["PlayerInfo", "run_playerctl", "get_player_info"]

import subprocess
from dataclasses import dataclass


@dataclass
class PlayerInfo:
    """Information about the current media player.
    
    Attributes:
        player: Name of the media player (e.g., 'spotify', 'firefox').
        title: Title of the currently playing track.
        artist: Artist name of the currently playing track.
        status: Playback status ('playing', 'paused', or 'stopped').
    """

    player: str
    title: str
    artist: str
    status: str


def run_playerctl(args: list[str]) -> str | None:
    """Run playerctl command and return output.
    
    Args:
        args: List of command line arguments to pass to playerctl.
    
    Returns:
        The stripped stdout from playerctl if successful, None if the command
        fails, times out, or playerctl is not found.
    
    Example:
        >>> run_playerctl(['metadata', '--format', '{{title}}'])
        'Song Title'
    """
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
    """Get current player information from the active MPRIS player.
    
    Queries playerctl for metadata about the currently active media player,
    including player name, track title, artist, and playback status.
    
    Returns:
        PlayerInfo object containing current player state, or None if no
        player is active or playerctl is unavailable.
    
    Example:
        >>> info = get_player_info()
        >>> if info:
        ...     print(f"{info.artist} - {info.title}")
        Artist Name - Song Title
    """
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

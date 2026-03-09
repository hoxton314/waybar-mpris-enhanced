"""Playerctl interaction for MPRIS module.

This module handles all communication with playerctl to retrieve
information about active MPRIS media players.
"""

__all__ = ["PlayerInfo", "run_playerctl", "select_best_player", "get_player_info"]

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


_STATUS_PRIORITY = {"playing": 0, "paused": 1, "stopped": 2}


def select_best_player() -> str | None:
    """Select the best player based on playback status.

    Enumerates all available MPRIS players and selects the one with the
    highest priority status: playing > paused > stopped.

    Returns:
        The name of the best player, or None if no players are available.
    """
    players_output = run_playerctl(["-l"])
    if not players_output:
        return None

    players = [p.strip() for p in players_output.splitlines() if p.strip()]
    if not players:
        return None

    best_player = None
    best_priority = len(_STATUS_PRIORITY)

    for player in players:
        status = run_playerctl(["--player", player, "status"])
        if status is None:
            continue
        priority = _STATUS_PRIORITY.get(status.lower(), len(_STATUS_PRIORITY))
        if priority < best_priority:
            best_priority = priority
            best_player = player

    return best_player


def get_player_info() -> PlayerInfo | None:
    """Get current player information from the active MPRIS player.

    Selects the best available player (playing > paused > stopped) and
    queries playerctl for its metadata including title, artist, and status.

    Returns:
        PlayerInfo object containing current player state, or None if no
        player is active or playerctl is unavailable.

    Example:
        >>> info = get_player_info()
        >>> if info:
        ...     print(f"{info.artist} - {info.title}")
        Artist Name - Song Title
    """
    player = select_best_player()
    if not player:
        return None

    title = run_playerctl(["--player", player, "metadata", "--format", "{{title}}"]) or "Unknown"
    artist = run_playerctl(["--player", player, "metadata", "--format", "{{artist}}"]) or "Unknown"
    status = run_playerctl(["--player", player, "status"]) or "Stopped"

    return PlayerInfo(
        player=player.lower(),
        title=title,
        artist=artist,
        status=status.lower(),
    )

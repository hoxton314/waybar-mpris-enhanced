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

# Browsers that embed media players — deprioritized vs dedicated music apps.
_BROWSER_PLAYERS = {"firefox", "chromium", "chrome", "google-chrome", "brave", "opera", "vivaldi", "epiphany"}


def _player_type_priority(player_name: str) -> int:
    """Return 0 for dedicated music apps, 1 for browsers."""
    return 1 if player_name.lower().split(".")[0] in _BROWSER_PLAYERS else 0


def select_best_player() -> str | None:
    """Select the best player based on playback status and player type.

    Enumerates all available MPRIS players and selects using:
      1. Playback status: playing > paused > stopped
      2. Player type: dedicated music app > browser

    Returns:
        The name of the best player, or None if no players are available.
    """
    players_output = run_playerctl(["-l"])
    if not players_output:
        return None

    players = [p.strip() for p in players_output.splitlines() if p.strip()]
    if not players:
        return None

    candidates = []
    for player in players:
        status = run_playerctl(["--player", player, "status"])
        if status is None:
            continue
        status_p = _STATUS_PRIORITY.get(status.lower(), len(_STATUS_PRIORITY))
        type_p = _player_type_priority(player)
        candidates.append((status_p, type_p, player))

    if not candidates:
        return None

    candidates.sort(key=lambda x: (x[0], x[1]))
    return candidates[0][2]


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

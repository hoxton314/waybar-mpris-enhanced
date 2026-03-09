"""Main entry point for MPRIS enhanced module.

This module provides Waybar-compatible JSON output for displaying
and controlling MPRIS media players.
"""

import argparse
import json
import subprocess

from . import __version__
from .components import (
    EndashComponent,
    InfoComponent,
    NextComponent,
    PlayComponent,
    PlayerIconComponent,
    PrevComponent,
)
from .components.base import ComponentArgs
from .constants import PLAYER_ICONS, STATUS_ICONS
from .playerctl import get_all_players, get_player_info, pin_player, run_playerctl, select_best_player

COMPONENTS = {
    "info": InfoComponent,
    "player-icon": PlayerIconComponent,
    "endash": EndashComponent,
    "prev": PrevComponent,
    "play": PlayComponent,
    "next": NextComponent,
}


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed command line arguments containing component
            selection and display options.
    """
    parser = argparse.ArgumentParser(
        description="Enhanced Waybar MPRIS module",
        prog="waybar-mpris-enhanced",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "component",
        nargs="?",
        default="info",
        choices=list(COMPONENTS.keys()) + ["select-player", "pick"],
        help="Component to display, or 'select-player'/'pick' for player selection",
    )
    parser.add_argument(
        "--scroll",
        action="store_true",
        help="Enable scrolling text for long titles (info component only)",
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=25,
        help="Maximum text length before truncating/scrolling (default: 25)",
    )
    parser.add_argument(
        "--scroll-speed",
        type=int,
        default=1,
        help="Number of characters to scroll per update (default: 1)",
    )

    return parser.parse_args()


def _run_picker() -> None:
    """Show a walker dmenu listing all active players; pin the selection."""
    players = get_all_players()
    if not players:
        return

    current = select_best_player()
    entries = []
    for player, status in players:
        player_icon = PLAYER_ICONS.get(player.lower().split(".")[0], PLAYER_ICONS["default"])
        status_icon = STATUS_ICONS.get(status, STATUS_ICONS["default"])
        title = run_playerctl(["--player", player, "metadata", "--format", "{{title}}"]) or "Unknown"
        artist = run_playerctl(["--player", player, "metadata", "--format", "{{artist}}"]) or ""
        label = f"{player_icon}  {player.title()}   {status_icon} {status.capitalize()}   {title}"
        if artist:
            label += f"  —  {artist}"
        entries.append(label)

    current_index = next((i for i, (p, _) in enumerate(players) if p == current), 0)

    try:
        result = subprocess.run(
            ["walker", "--dmenu", "--index", "--current", str(current_index), "--placeholder", "Select media source"],
            input="\n".join(entries),
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return

    if result.returncode != 0 or not result.stdout.strip():
        return

    try:
        index = int(result.stdout.strip())
        pin_player(players[index][0])
    except (ValueError, IndexError):
        pass


def main() -> None:
    """Main entry point for the MPRIS enhanced module.

    Parses command line arguments, retrieves current player information,
    renders the requested component, and outputs JSON for Waybar consumption.

    The function exits with status 0 on success.
    """
    args = parse_args()

    component_args = ComponentArgs(
        scroll=args.scroll,
        max_length=args.max_length,
        scroll_speed=args.scroll_speed,
    )

    if args.component == "select-player":
        player = select_best_player()
        print(player or "")
        return

    if args.component == "pick":
        _run_picker()
        return

    component_class = COMPONENTS[args.component]
    component = component_class(component_args)

    info = get_player_info()
    output = component.render(info)

    print(json.dumps(output.to_dict()))


if __name__ == "__main__":
    main()

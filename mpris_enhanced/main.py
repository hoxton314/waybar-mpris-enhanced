"""Main entry point for MPRIS enhanced module."""

import argparse
import json

from .components import (
    EndashComponent,
    InfoComponent,
    NextComponent,
    PlayComponent,
    PlayerIconComponent,
    PrevComponent,
)
from .components.base import ComponentArgs
from .playerctl import get_player_info

COMPONENTS = {
    "info": InfoComponent,
    "player-icon": PlayerIconComponent,
    "endash": EndashComponent,
    "prev": PrevComponent,
    "play": PlayComponent,
    "next": NextComponent,
}


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Enhanced Waybar MPRIS module")
    parser.add_argument(
        "component",
        nargs="?",
        default="info",
        choices=list(COMPONENTS.keys()),
        help="Component to display",
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


def main() -> None:
    """Main entry point."""
    args = parse_args()

    component_args = ComponentArgs(
        scroll=args.scroll,
        max_length=args.max_length,
        scroll_speed=args.scroll_speed,
    )

    component_class = COMPONENTS[args.component]
    component = component_class(component_args)

    info = get_player_info()
    output = component.render(info)

    print(json.dumps(output.to_dict()))


if __name__ == "__main__":
    main()

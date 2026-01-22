"""Info display components (info, player-icon, endash).

Components for displaying media information including player icons,
track titles, and separator elements.
"""

from ..constants import PLAYER_ICONS
from ..playerctl import PlayerInfo
from ..utils import escape_pango, get_scrolling_text, truncate_text
from .base import Component, ComponentOutput


class InfoComponent(Component):
    """Main info component showing player icon and track title.

    Displays the current media player icon and track title with optional
    scrolling for long titles. Includes tooltip with full information.
    """

    name = "info"

    def render(self, info: PlayerInfo | None) -> ComponentOutput:
        if not info:
            return ComponentOutput(
                text="",
                tooltip="No media playing",
                class_="stopped",
            )

        player_icon = PLAYER_ICONS.get(info.player, PLAYER_ICONS["default"])

        if self.args.scroll:
            title = get_scrolling_text(
                info.title,
                self.args.max_length,
                self.args.scroll_speed,
            )
        else:
            title = truncate_text(info.title, self.args.max_length)

        # Escape title, artist, and player name for Pango markup
        escaped_title = escape_pango(title)
        escaped_artist = escape_pango(info.artist)
        escaped_player = escape_pango(info.player.title())
        escaped_full_title = escape_pango(info.title)

        text = f"{player_icon}  {escaped_title}"
        tooltip = f"{player_icon} {escaped_player}: {escaped_artist} - {escaped_full_title}"

        return ComponentOutput(
            text=text,
            tooltip=tooltip,
            class_=f"media-info {info.status}",
        )


class PlayerIconComponent(Component):
    """Player icon only component.

    Displays only the icon representing the current media player.
    """

    name = "player-icon"

    def render(self, info: PlayerInfo | None) -> ComponentOutput:
        if not info:
            return self.render_hidden()

        player_icon = PLAYER_ICONS.get(info.player, PLAYER_ICONS["default"])

        return ComponentOutput(
            text=player_icon,
            class_="media-info",
        )


class EndashComponent(Component):
    """Endash separator component.

    Displays a simple dash separator between other components.
    Hidden when no player is active.
    """

    name = "endash"

    def render(self, info: PlayerInfo | None) -> ComponentOutput:
        if not info:
            return self.render_hidden()

        return ComponentOutput(
            text="-",
            class_="endash",
        )

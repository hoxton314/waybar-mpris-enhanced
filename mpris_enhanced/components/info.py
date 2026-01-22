"""Info display components (info, player-icon, endash)."""

from ..constants import PLAYER_ICONS
from ..playerctl import PlayerInfo
from ..utils import get_scrolling_text, truncate_text
from .base import Component, ComponentOutput


class InfoComponent(Component):
    """Main info component showing player icon and track title."""

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

        text = f"{player_icon}  {title}"
        tooltip = f"{player_icon} {info.player.title()}: {info.artist} - {info.title}"

        return ComponentOutput(
            text=text,
            tooltip=tooltip,
            class_=f"media-info {info.status}",
        )


class PlayerIconComponent(Component):
    """Player icon only component."""

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
    """Endash separator component."""

    name = "endash"

    def render(self, info: PlayerInfo | None) -> ComponentOutput:
        if not info:
            return self.render_hidden()

        return ComponentOutput(
            text="-",
            class_="endash",
        )

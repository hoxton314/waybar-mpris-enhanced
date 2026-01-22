"""Control button components (prev, play, next)."""

from ..constants import CONTROL_ICONS
from ..playerctl import PlayerInfo
from .base import Component, ComponentOutput


class PrevComponent(Component):
    """Previous track button component."""

    name = "prev"

    def render(self, info: PlayerInfo | None) -> ComponentOutput:
        if not info:
            return self.render_hidden()

        return ComponentOutput(
            text=CONTROL_ICONS["prev"],
            class_="media-button prev",
        )


class PlayComponent(Component):
    """Play/pause button component."""

    name = "play"

    def render(self, info: PlayerInfo | None) -> ComponentOutput:
        if not info:
            return self.render_hidden()

        # Show Pause icon when playing, Play icon when paused
        status_icon = CONTROL_ICONS["pause"] if info.status == "Playing" else CONTROL_ICONS["play"]

        return ComponentOutput(
            text=status_icon,
            class_=f"media-button play {info.status.lower()}",
        )


class NextComponent(Component):
    """Next track button component."""

    name = "next"

    def render(self, info: PlayerInfo | None) -> ComponentOutput:
        if not info:
            return self.render_hidden()

        return ComponentOutput(
            text=CONTROL_ICONS["next"],
            class_="media-button next",
        )

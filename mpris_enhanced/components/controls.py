"""Control button components (prev, play, next).

Components for rendering media playback control buttons (previous,
play/pause, next) with appropriate icons and states.
"""

from ..constants import CONTROL_ICONS
from ..playerctl import PlayerInfo
from .base import Component, ComponentOutput


class PrevComponent(Component):
    """Previous track button component.
    
    Displays a button to skip to the previous track.
    """

    name = "prev"

    def render(self, info: PlayerInfo | None) -> ComponentOutput:
        if not info:
            return self.render_hidden()

        return ComponentOutput(
            text=CONTROL_ICONS["prev"],
            class_="media-button prev",
        )


class PlayComponent(Component):
    """Play/pause button component.
    
    Displays a play or pause icon based on current playback status.
    Shows pause icon when playing, play icon when paused.
    """

    name = "play"

    def render(self, info: PlayerInfo | None) -> ComponentOutput:
        if not info:
            return self.render_hidden()

        # Show Pause icon when playing, Play icon when paused
        status_icon = (
            CONTROL_ICONS["pause"]
            if info.status == "playing"
            else CONTROL_ICONS["play"]
        )

        return ComponentOutput(
            text=status_icon,
            class_=f"media-button play {info.status}",
        )


class NextComponent(Component):
    """Next track button component.
    
    Displays a button to skip to the next track.
    """

    name = "next"

    def render(self, info: PlayerInfo | None) -> ComponentOutput:
        if not info:
            return self.render_hidden()

        return ComponentOutput(
            text=CONTROL_ICONS["next"],
            class_="media-button next",
        )

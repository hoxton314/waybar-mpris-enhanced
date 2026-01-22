"""Base component class for MPRIS module."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..playerctl import PlayerInfo


@dataclass
class ComponentOutput:
    """Output structure for waybar custom module."""

    text: str
    class_: str
    tooltip: str | None = None

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary for JSON output."""
        result = {"text": self.text, "class": self.class_}
        if self.tooltip is not None:
            result["tooltip"] = self.tooltip
        return result


@dataclass
class ComponentArgs:
    """Arguments passed to components."""

    scroll: bool = False
    max_length: int = 25
    scroll_speed: int = 1


class Component(ABC):
    """Base class for all components."""

    def __init__(self, args: ComponentArgs | None = None):
        self.args = args or ComponentArgs()

    @abstractmethod
    def render(self, info: PlayerInfo | None) -> ComponentOutput:
        """Render the component output."""
        ...

    def render_hidden(self) -> ComponentOutput:
        """Render hidden output when no player is active."""
        return ComponentOutput(text="", class_="custom-enhanced-mpris-hidden")

"""Base component class for MPRIS module.

Provides abstract base classes and data structures for all MPRIS
components that render Waybar-compatible JSON output.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..playerctl import PlayerInfo


@dataclass
class ComponentOutput:
    """Output structure for waybar custom module.
    
    Attributes:
        text: The text to display in the Waybar module.
        class_: CSS class name(s) for styling the module.
        tooltip: Optional tooltip text shown on hover.
    """

    text: str
    class_: str
    tooltip: str | None = None

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary for JSON output.
        
        Returns:
            Dictionary with 'text', 'class', and optionally 'tooltip' keys
            for Waybar custom module JSON format.
        """
        result = {"text": self.text, "class": self.class_}
        if self.tooltip is not None:
            result["tooltip"] = self.tooltip
        return result


@dataclass
class ComponentArgs:
    """Arguments passed to components.
    
    Attributes:
        scroll: Enable scrolling animation for long text.
        max_length: Maximum text length before truncation/scrolling.
        scroll_speed: Characters to scroll per update cycle.
    """

    scroll: bool = False
    max_length: int = 25
    scroll_speed: int = 1


class Component(ABC):
    """Base class for all components.
    
    All MPRIS components inherit from this class and must implement
    the render() method to provide Waybar-compatible output.
    """

    def __init__(self, args: ComponentArgs | None = None) -> None:
        """Initialize component with optional arguments.
        
        Args:
            args: Component configuration arguments. Uses defaults if None.
        """
        self.args = args or ComponentArgs()

    @abstractmethod
    def render(self, info: PlayerInfo | None) -> ComponentOutput:
        """Render the component output.
        
        Args:
            info: Current player information, or None if no player active.
        
        Returns:
            ComponentOutput with text, CSS class, and optional tooltip.
        """
        ...

    def render_hidden(self) -> ComponentOutput:
        """Render hidden output when no player is active.
        
        Returns:
            ComponentOutput with empty text and hidden CSS class.
        """
        return ComponentOutput(text="", class_="custom-enhanced-mpris-hidden")

"""Utility functions for MPRIS module.

Provides text processing utilities including Pango markup escaping,
text truncation, and scrolling text animation with state persistence.
"""

__all__ = [
    "truncate_text",
    "get_scroll_state_file",
    "get_scrolling_text",
    "escape_pango",
]

import hashlib
import os
import tempfile


def escape_pango(text: str) -> str:
    """Escape special characters for Pango markup.
    
    Args:
        text: Input text that may contain special characters.
    
    Returns:
        Text with HTML/XML special characters escaped for safe use in
        Pango markup (used by Waybar for tooltips and formatting).
    
    Example:
        >>> escape_pango("Rock & Roll <3")
        'Rock &amp; Roll &lt;3'
    """
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("'", "&apos;")
        .replace('"', "&quot;")
    )


def truncate_text(text: str, max_len: int) -> str:
    """Truncate text to max length with ellipsis.
    
    Args:
        text: Input text to truncate.
        max_len: Maximum length of output string (including ellipsis).
    
    Returns:
        Original text if shorter than max_len, otherwise truncated text
        with a trailing ellipsis character (…).
    
    Example:
        >>> truncate_text("Very Long Song Title", 10)
        'Very Long…'
    """
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def get_scroll_state_file(text: str) -> str:
    """Get the path to the scroll state file for the given text.
    
    Creates a unique temporary file path based on the text content hash,
    used to persist scroll position across invocations.
    
    Args:
        text: The text being scrolled (used to generate unique hash).
    
    Returns:
        Absolute path to the scroll state file in the system temp directory.
    """
    text_hash = hashlib.sha256(text.encode()).hexdigest()[:8]
    return os.path.join(
        tempfile.gettempdir(),
        f"waybar-mpris-scroll-{text_hash}",
    )


def get_scrolling_text(text: str, max_len: int, scroll_speed: int = 1) -> str:
    """Get scrolling text with state persistence.
    
    Returns a sliding window of text that shifts on each call, creating
    a marquee/scrolling effect. The scroll position is persisted in a
    temporary file so it continues smoothly across invocations.
    
    Args:
        text: The full text to scroll.
        max_len: Maximum length of the visible window.
        scroll_speed: Number of characters to advance per call (default: 1).
    
    Returns:
        A max_len substring of the text, shifted based on the current
        scroll position. If text fits within max_len, returns unchanged.
    
    Example:
        >>> # First call
        >>> get_scrolling_text("Long scrolling title", 10, 1)
        'Long scrol'
        >>> # Second call (shifted by 1)
        >>> get_scrolling_text("Long scrolling title", 10, 1)
        'ong scroll'
    """
    if len(text) <= max_len:
        return text

    # Add separator for continuous scrolling effect
    padded_text = text + "   ·   "
    total_len = len(padded_text)

    state_file = get_scroll_state_file(text)

    # Read current position
    try:
        with open(state_file) as f:
            position = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        position = 0

    # Calculate the visible window
    visible_text = "".join(
        padded_text[(position + i) % total_len] for i in range(max_len)
    )

    # Update position for next call (atomic write to prevent race conditions)
    new_position = (position + scroll_speed) % total_len
    try:
        tmp_file = state_file + ".tmp"
        with open(tmp_file, "w") as f:
            f.write(str(new_position))
        os.replace(tmp_file, state_file)
    except OSError:
        pass

    return visible_text

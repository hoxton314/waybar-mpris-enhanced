"""Utility functions for MPRIS module."""

import hashlib
import os
import tempfile


def truncate_text(text: str, max_len: int) -> str:
    """Truncate text to max length with ellipsis."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def get_scroll_state_file(text: str) -> str:
    """Get the path to the scroll state file for the given text."""
    text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
    return os.path.join(
        tempfile.gettempdir(),
        f"waybar-mpris-scroll-{text_hash}",
    )


def get_scrolling_text(text: str, max_len: int, scroll_speed: int = 1) -> str:
    """
    Get scrolling text with state persistence.
    Returns a window of text that shifts on each call.
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
    visible_text = ""
    for i in range(max_len):
        idx = (position + i) % total_len
        visible_text += padded_text[idx]

    # Update position for next call
    new_position = (position + scroll_speed) % total_len
    try:
        with open(state_file, "w") as f:
            f.write(str(new_position))
    except OSError:
        pass

    return visible_text

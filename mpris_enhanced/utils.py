"""Utility functions for MPRIS module."""

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
    """Escape special characters for Pango markup."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("'", "&apos;")
        .replace('"', "&quot;")
    )


def truncate_text(text: str, max_len: int) -> str:
    """Truncate text to max length with ellipsis."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def get_scroll_state_file(text: str) -> str:
    """Get the path to the scroll state file for the given text."""
    text_hash = hashlib.sha256(text.encode()).hexdigest()[:8]
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

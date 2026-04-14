from dataclasses import dataclass
from typing import Literal


@dataclass(slots=True)
class Note:
    """Store a single note with metadata."""

    id: int
    """Unique note identifier from database."""

    text: str
    """Note content text."""

    created_at: str
    """ISO 8601 timestamp when note was created."""

    has_image: bool = False
    """Whether note has attached image(s)."""


@dataclass(slots=True)
class NoteImage:
    """Store Telegram file_id for note image in specific size."""

    note_id: int
    """Foreign key to parent note."""

    size: Literal["small", "large"]
    """Image size variant (small for preview, large for full)."""

    file_id: str
    """Telegram file_id for retrieving image."""

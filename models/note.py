from dataclasses import dataclass
from typing import Literal


@dataclass
class Note:
    id: int
    text: str
    created_at: str
    has_image: bool = False


@dataclass
class NoteImage:
    note_id: int
    size: Literal["small", "large"]
    file_id: str

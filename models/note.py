from dataclasses import dataclass


@dataclass
class Note:
    id: int
    text: str
    created_at: str
    has_image: bool = False


@dataclass
class NoteImage:
    note_id: int
    size: str
    file_id: str

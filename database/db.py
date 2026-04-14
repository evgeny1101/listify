import datetime
import inspect
from typing import Literal

import aiosqlite

from config import DB_PATH
from models.note import Note, NoteImage


async def _disable_foreign_keys(db: aiosqlite.Connection) -> None:
    result = db.execute("PRAGMA foreign_keys = OFF")
    if inspect.isawaitable(result):
        await result


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await _disable_foreign_keys(db)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS note_images (
                note_id INTEGER,
                size TEXT CHECK(size IN ('small', 'large')),
                file_id TEXT NOT NULL,
                PRIMARY KEY (note_id, size),
                FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
            )
        """)
        await db.commit()


async def add_note(text: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        await _disable_foreign_keys(db)
        cursor = await db.execute(
            "INSERT INTO notes (text, created_at) VALUES (?, ?)",
            (text, datetime.datetime.now(datetime.UTC).isoformat()),
        )
        await db.commit()
        return cursor.lastrowid


async def get_notes() -> list[Note]:
    async with aiosqlite.connect(DB_PATH) as db:
        await _disable_foreign_keys(db)
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT n.id, n.text, n.created_at,
                   EXISTS(SELECT 1 FROM note_images WHERE note_id = n.id) as has_image
            FROM notes n ORDER BY n.id
        """) as cursor:
            rows = await cursor.fetchall()
            return [
                Note(row["id"], row["text"], row["created_at"], bool(row["has_image"]))
                for row in rows
            ]


async def get_note(note_id: int) -> Note | None:
    async with aiosqlite.connect(DB_PATH) as db:
        await _disable_foreign_keys(db)
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT n.id, n.text, n.created_at,
                   EXISTS(SELECT 1 FROM note_images WHERE note_id = n.id) as has_image
            FROM notes n WHERE n.id = ?
        """,
            (note_id,),
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return Note(
                    row["id"], row["text"], row["created_at"], bool(row["has_image"])
                )
            return None


async def delete_note(note_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        await _disable_foreign_keys(db)
        cursor = await db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        await db.commit()
        return cursor.rowcount > 0


async def add_note_image(
    note_id: int, size: Literal["small", "large"], file_id: str
) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await _disable_foreign_keys(db)
        await db.execute(
            "INSERT OR REPLACE INTO note_images (note_id, size, file_id) VALUES (?, ?, ?)",
            (note_id, size, file_id),
        )
        await db.commit()


async def get_note_images(note_id: int) -> list[NoteImage]:
    async with aiosqlite.connect(DB_PATH) as db:
        await _disable_foreign_keys(db)
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT note_id, size, file_id FROM note_images WHERE note_id = ?",
            (note_id,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [
                NoteImage(row["note_id"], row["size"], row["file_id"]) for row in rows
            ]


async def delete_note_images(note_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await _disable_foreign_keys(db)
        await db.execute("DELETE FROM note_images WHERE note_id = ?", (note_id,))
        await db.commit()

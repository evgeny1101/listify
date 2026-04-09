import aiosqlite
from config import DB_PATH
from models.note import Note
from datetime import datetime


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


async def add_note(text: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO notes (text, created_at) VALUES (?, ?)",
            (text, datetime.now().isoformat()),
        )
        await db.commit()
        return cursor.lastrowid


async def get_notes() -> list[Note]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT id, text, created_at FROM notes ORDER BY id"
        ) as cursor:
            rows = await cursor.fetchall()
            return [Note(row["id"], row["text"], row["created_at"]) for row in rows]


async def delete_note(note_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        await db.commit()
        return cursor.rowcount > 0

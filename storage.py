import os
import sqlite3
from contextlib import contextmanager


DATABASE_PATH = os.getenv("DATABASE_PATH", "chat_history.db")


@contextmanager
def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel TEXT NOT NULL,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_chat_lookup
            ON chat_messages (channel, conversation_id, id)
            """
        )


def add_message(channel, conversation_id, role, content):
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO chat_messages (channel, conversation_id, role, content)
            VALUES (?, ?, ?, ?)
            """,
            (channel, conversation_id, role, content),
        )


def trim_conversation(channel, conversation_id, keep_last):
    with get_connection() as connection:
        connection.execute(
            """
            DELETE FROM chat_messages
            WHERE id IN (
                SELECT id
                FROM chat_messages
                WHERE channel = ? AND conversation_id = ?
                ORDER BY id DESC
                LIMIT -1 OFFSET ?
            )
            """,
            (channel, conversation_id, keep_last),
        )


def get_recent_history(channel, conversation_id, limit):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT role, content
            FROM chat_messages
            WHERE channel = ? AND conversation_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (channel, conversation_id, limit),
        ).fetchall()

    rows.reverse()
    return [{"role": role, "content": content} for role, content in rows]

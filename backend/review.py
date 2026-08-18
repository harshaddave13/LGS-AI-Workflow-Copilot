import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("database/reviews.db")


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            field_name TEXT NOT NULL,
            original_value TEXT,
            reviewed_value TEXT,
            status TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_review(
    field_name,
    original_value,
    reviewed_value,
    status
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO reviews (
            field_name,
            original_value,
            reviewed_value,
            status,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        field_name,
        original_value,
        reviewed_value,
        status,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

def get_reviews():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            field_name,
            original_value,
            reviewed_value,
            status,
            timestamp
        FROM reviews
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows
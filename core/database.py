import sqlite3
from pathlib import Path

DB_PATH = Path("expenses.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_transaction(title, amount, category, date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO transactions (title, amount, category, date)
    VALUES (?, ?, ?, ?)
    """, (title, amount, category, date))

    conn.commit()
    conn.close()


def get_transactions():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM transactions ORDER BY date DESC")
    data = cursor.fetchall()

    conn.close()
    return data


def delete_transaction(title, amount, category, date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM transactions WHERE title=? AND amount=? AND category=? AND date=?",
        (title, amount, category, date)
    )

    conn.commit()
    conn.close()
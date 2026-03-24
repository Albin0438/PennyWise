import sqlite3
from pathlib import Path
import shutil
import os
from datetime import datetime
from tkinter import filedialog, messagebox

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

def backup_database():
    db_file = "pennywise.db"

    if not os.path.exists(db_file):
        messagebox.showerror("Error", "Database file not found!")
        return

    # Ask user where to save
    file_path = filedialog.asksaveasfilename(
        defaultextension=".db",
        filetypes=[("Database Files", "*.db")],
        title="Save Backup As"
    )

    if not file_path:
        return  # user cancelled

    try:
        shutil.copy(db_file, file_path)
        messagebox.showinfo("Success", "Backup created successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))
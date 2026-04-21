import csv
import sqlite3

DB_PATH = "expenses.db"

def import_csv(file_path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    inserted = 0
    skipped = 0

    with open(file_path, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            title = row.get('title') or row.get('Title')
            amount = row.get('amount') or row.get('Amount')
            category = row.get('category') or row.get('Category')
            date = row.get('date') or row.get('Date')

            # 🔍 Check duplicate
            cursor.execute("""
                SELECT 1 FROM transactions
                WHERE title=? AND amount=? AND category=? AND date=?
            """, (title, float(amount), category, date))

            if cursor.fetchone():
                skipped += 1
            else:
                cursor.execute("""
                    INSERT INTO transactions (title, amount, category, date)
                    VALUES (?, ?, ?, ?)
                """, (title, float(amount), category, date))
                inserted += 1

    conn.commit()
    conn.close()

    return inserted, skipped
import tkinter as tk
from tkinter import messagebox
from core.database import add_transaction
from datetime import datetime


class TransactionForm:
    def __init__(self, parent, refresh_callback):
        # Create popup window
        self.top = tk.Toplevel(parent)
        self.top.title("Add Expense")
        self.top.geometry("300x200")
        self.top.resizable(False, False)

        self.refresh_callback = refresh_callback

        # Frame (for layout)
        frame = tk.Frame(self.top)
        frame.pack(pady=20)

        # Title
        tk.Label(frame, text="Title").grid(row=0, column=0, pady=5)
        self.title_entry = tk.Entry(frame)
        self.title_entry.grid(row=0, column=1, pady=5)

        # Amount
        tk.Label(frame, text="Amount").grid(row=1, column=0, pady=5)
        self.amount_entry = tk.Entry(frame)
        self.amount_entry.grid(row=1, column=1, pady=5)

        # Category
        tk.Label(frame, text="Category").grid(row=2, column=0, pady=5)
        self.category_entry = tk.Entry(frame)
        self.category_entry.grid(row=2, column=1, pady=5)

        # Save Button
        tk.Button(self.top, text="Save", command=self.save, width=15).pack(pady=10)

    def save(self):
        try:
            title = self.title_entry.get()
            amount = float(self.amount_entry.get())
            category = self.category_entry.get()
            date = datetime.now().strftime("%Y-%m-%d")

            if not title:
                messagebox.showerror("Error", "Title required")
                return

            add_transaction(title, amount, category, date)

            messagebox.showinfo("Success", "Expense added!")

            self.refresh_callback()
            self.top.destroy()

        except Exception as e:
            print("Error:", e)
            messagebox.showerror("Error", str(e))
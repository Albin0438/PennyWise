import tkinter as tk
from datetime import datetime
from ui.transaction_form import TransactionForm
from core.database import get_transactions

class ExpenseApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PennyWise 💰")
        self.root.geometry("800x500")

        # Search
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=5)

        tk.Label(search_frame, text="Search:").pack(side="left")
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side="left", padx=5)
        tk.Button(search_frame, text="Go", command=self.search_data).pack(side="left")

        # Filter
        categories = ["All", "Food", "Transport", "Shopping", "Other"]  # example categories
        self.category_var = tk.StringVar(value="All")

        filter_frame = tk.Frame(self.root)
        filter_frame.pack(pady=5)

        tk.Label(filter_frame, text="Filter Category:").pack(side="left")
        tk.OptionMenu(filter_frame, self.category_var, *categories, command=lambda e: self.load_data()).pack(side="left")

        # Title label
        title = tk.Label(
            self.root,
            text="PennyWise Expense Tracker",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=20)

        # Add button
        add_btn = tk.Button(
            self.root,
            text="Add Expense",
            command=self.add_expense
        )
        add_btn.pack(pady=10)

        from tkinter import ttk

        # Table
        self.tree = ttk.Treeview(self.root, columns=("Title", "Amount", "Category"), show="headings")

        self.tree.heading("Title", text="Title")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Category", text="Category")

        self.tree.pack(pady=20, fill="both", expand=True)

        delete_btn = tk.Button(
            self.root,
            text="Delete Selected",
            command=self.delete_selected
        )
        delete_btn.pack(pady=5)

        self.total_label = tk.Label(self.root, text="Total: ₹0", font=("Arial", 12, "bold"))
        self.total_label.pack(pady=10)

        self.insight_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.insight_label.pack(pady=5)

        self.load_data()

    def add_expense(self):
        TransactionForm(self.root, self.load_data)

    def run(self):
        self.root.mainloop()
    
    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = get_transactions()
        total = 0

        # Calculate category totals
        category_totals = {}
        for row in data:
            category_totals[row[3]] = category_totals.get(row[3], 0) + row[2]

        # Update insight label
        if category_totals:
            top_category = max(category_totals, key=category_totals.get)
            self.insight_label.config(text=f"Top spending category: {top_category} (₹{category_totals[top_category]})")
        else:
            self.insight_label.config(text="")

        category_filter = self.category_var.get()
        for row in data:
            if category_filter != "All" and row[3] != category_filter:
                continue
            self.tree.insert("", "end", values=(row[1], f"₹{row[2]}", row[3]))
            total += row[2]

        self.total_label.config(text=f"Total: ₹{total}")

    def delete_selected(self):
        selected = self.tree.selection()

        if not selected:
            return

        item = self.tree.item(selected[0])
        title, amount, category = item["values"]

        # Remove ₹ symbol
        amount = float(str(amount).replace("₹", ""))

        from core.database import delete_transaction
        delete_transaction(title, amount, category)

        self.load_data()

    def search_data(self):
        query = self.search_entry.get().lower()
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = get_transactions()
        total = 0

        for row in data:
            if query in row[1].lower() or query in str(row[3]).lower():
                self.tree.insert("", "end", values=(row[1], f"₹{row[2]}", row[3]))
                total += row[2]

        self.total_label.config(text=f"Total: ₹{total}")

        # Update top category based on filtered results
        category_totals = {}
        for row in data:
            if query in row[1].lower() or query in str(row[3]).lower():
                category_totals[row[3]] = category_totals.get(row[3], 0) + row[2]

        if category_totals:
            top_category = max(category_totals, key=category_totals.get)
            self.insight_label.config(text=f"Top spending category: {top_category} (₹{category_totals[top_category]})")
        else:
            self.insight_label.config(text="")
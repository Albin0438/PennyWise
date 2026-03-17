import tkinter as tk
from tkinter import ttk
from datetime import datetime
from ui.transaction_form import TransactionForm
from core.database import get_transactions

class ExpenseApp:
    BG = "#1e1e1e"
    FG = "#ffffff"
    ACCENT = "#00adb5"
    ENTRY_BG = "#2c2c2c"
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PennyWise 💰")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e1e")
        style = ttk.Style()

        style.theme_use("default")

        style.configure(
            "Treeview",
            background="#2c2c2c",
            foreground="white",
            fieldbackground="#2c2c2c",
            rowheight=25
        )

        style.map("Treeview", background=[("selected", "#00adb5")])

        style.configure("green.Horizontal.TProgressbar", foreground="green", background="green")
        style.configure("yellow.Horizontal.TProgressbar", foreground="orange", background="orange")
        style.configure("red.Horizontal.TProgressbar", foreground="red", background="red")

        # Search
        search_frame = tk.Frame(self.root, bg=self.BG)
        search_frame.pack(pady=5)

        tk.Label(search_frame, text="Search:",  bg=self.BG, fg=self.FG).pack(side="left")
        self.search_entry = tk.Entry(search_frame, bg=self.ENTRY_BG, fg=self.FG, insertbackground="white")
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.live_search)
        tk.Button(search_frame, text="Go", command=self.search_data, bg=self.ACCENT, fg="black", activebackground="#00cfd5", relief="flat").pack(side="left")

        # Filter
        categories = ["All", "Food", "Transport", "Shopping", "Other"]  # example categories
        self.category_var = tk.StringVar(value="All")

        filter_frame = tk.Frame(self.root, bg=self.BG)
        filter_frame.pack(pady=5)

        tk.Label(filter_frame, text="Filter Category:",  bg=self.BG, fg=self.FG).pack(side="left")
        menu = tk.OptionMenu(filter_frame, self.category_var, *categories, command=lambda e: self.load_data())
        menu.config(bg=self.ENTRY_BG, fg=self.FG, activebackground=self.ACCENT)
        menu["menu"].config(bg=self.ENTRY_BG, fg=self.FG)
        menu.pack(side="left")

        # Title label
        title = tk.Label(
            self.root,
            text="PennyWise Expense Tracker",
            bg=self.BG,
            fg=self.FG,
            font=("Arial", 18, "bold")
        )
        title.pack(pady=20)

        # Add button
        add_btn = tk.Button(
            self.root,
            text="Add Expense",
            command=self.add_expense,
            bg=self.ACCENT,
            fg="black",
            activebackground="#00cfd5",
            relief="flat"
        )
        add_btn.pack(pady=10)

        # Theme Toggle button
        self.theme = "dark"  # default theme
        toggle_btn = tk.Button(
            self.root,
            text="Switch to Light Mode",
            command=self.toggle_theme,
            bg=self.ACCENT,
            fg="black",
            activebackground="#00cfd5",
            relief="flat"
        )
        toggle_btn.pack(pady=5)
        self.toggle_btn = toggle_btn  # keep reference

        # Table
        self.tree = ttk.Treeview(self.root, columns=("Title", "Amount", "Category", "Date"), show="headings")

        self.tree.heading("Title", text="Title")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Date", text="Date")

        self.tree.pack(pady=20, fill="both", expand=True)

        # Delete
        delete_btn = tk.Button(
            self.root,
            text="Delete Selected",
            command=self.delete_selected,
            bg=self.ACCENT,
            fg="black",
            activebackground="#00cfd5",
            relief="flat"
        )
        delete_btn.pack(pady=5)
        
        # Graph
        graph_btn = tk.Button(
            self.root,
            text="Show Graph 📊",
            command=self.show_graph,
            bg=self.ACCENT,
            fg="black",
            activebackground="#00cfd5",
            relief="flat"
        )
        graph_btn.pack(pady=5)
        
        # Export
        export_btn = tk.Button(
            self.root,
            text="Export to CSV 📁",
            command=self.export_csv,
            bg=self.ACCENT,
            fg="black",
            activebackground="#00cfd5",
            relief="flat"
        )
        export_btn.pack(pady=5)

        # Style Button
        self.style_button(add_btn)
        self.style_button(delete_btn)
        self.style_button(graph_btn)
        self.style_button(export_btn)
        self.style_button(self.toggle_btn)

        # Total + Insight
        info_frame = tk.Frame(self.root, bg=self.BG)
        info_frame.pack(pady=10)

        self.total_label = tk.Label(info_frame, text="Total: ₹0", bg=self.BG, fg=self.FG, font=("Arial", 12, "bold"))
        self.total_label.pack()

        self.insight_label = tk.Label(info_frame, text="", bg=self.BG, fg=self.FG, font=("Arial", 12))
        self.insight_label.pack()

        # Budget

        budget_frame = tk.Frame(self.root, bg=self.BG)
        budget_frame.pack(pady=5)

        tk.Label(budget_frame, text="Monthly Budget:", bg=self.BG, fg=self.FG).pack(side="left")

        self.budget_entry = tk.Entry(budget_frame, bg=self.ENTRY_BG, fg=self.FG, insertbackground="white")
        self.budget_entry.pack(side="left", padx=5)

        tk.Button(budget_frame, text="Set", command=self.set_budget, bg=self.ACCENT, fg="black", activebackground="#00cfd5", relief="flat").pack(side="left")

        # Progress Bar UI
        tk.Label(self.root, text="Budget Usage", bg=self.BG, fg=self.FG).pack()
        self.progress = ttk.Progressbar(
            self.root,
            orient="horizontal",
            length=300,
            mode="determinate"
        )
        self.progress.pack(pady=5)

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
            
            from datetime import datetime

            formatted_date = datetime.strptime(row[4], "%Y-%m-%d").strftime("%d-%m-%Y")

            self.tree.insert(
                "",
                "end",
                values=(row[1], f"₹{row[2]}", row[3], formatted_date)
            )
            total += row[2]

        self.total_label.config(text=f"Total: ₹{total}")

        if hasattr(self, "budget") and self.budget > 0:
            percent = (total / self.budget) * 100
            self.progress["value"] = percent

            # Change color based on usage
            if percent < 70:
                self.progress.configure(style="green.Horizontal.TProgressbar")
            elif percent < 100:
                self.progress.configure(style="yellow.Horizontal.TProgressbar")
            else:
                self.progress.configure(style="red.Horizontal.TProgressbar")
        else:
            self.progress["value"] = 0

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

        if not query:
            self.load_data()
            return
        
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = get_transactions()
        total = 0

        for row in data:
            if query in row[1].lower() or query in str(row[3]).lower():
                formatted_date = datetime.strptime(row[4], "%Y-%m-%d").strftime("%d-%m-%Y")

                self.tree.insert(
                    "",
                    "end",
                    values=(row[1], f"₹{row[2]}", row[3], formatted_date)
                )
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

    def show_graph(self):
        import matplotlib.pyplot as plt
        from collections import defaultdict
        from datetime import datetime

        data = get_transactions()

        daily_totals = defaultdict(float)

        for row in data:
            date = row[4]
            amount = row[2]

            # convert to datetime object
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            daily_totals[date_obj] += amount

        # sort properly
        dates = sorted(daily_totals.keys())
        amounts = [daily_totals[d] for d in dates]

        # convert back to readable format
        labels = [d.strftime("%d-%m") for d in dates]

        plt.figure()
        plt.plot(labels, amounts, marker='o')
        plt.title("Spending Over Time")
        plt.xlabel("Date")
        plt.ylabel("Amount (₹)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def export_csv(self):
        import csv
        from tkinter import messagebox, filedialog

        data = get_transactions()

        # Ask user where to save
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )

        # If user cancels → do nothing
        if not file_path:
            return

        try:
            with open(file_path, "w", newline="") as file:
                writer = csv.writer(file)

                # Header
                writer.writerow(["Title", "Amount", "Category", "Date"])

                # Data
                for row in data:
                    writer.writerow([row[1], row[2], row[3], row[4]])

            messagebox.showinfo("Success", "Data exported successfully!")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def live_search(self, event):
        self.search_data()

    def set_budget(self):
        try:
            self.budget = float(self.budget_entry.get())
            self.load_data()
        except:
            self.budget = 0

    def style_button(self, btn):
        btn.config(cursor="hand2")
        btn.bind("<Enter>", lambda e: btn.config(bg="#00cfd5"))
        btn.bind("<Leave>", lambda e: btn.config(bg=self.ACCENT))

    def toggle_theme(self):
        if self.theme == "dark":
            self.BG = "#ffffff"
            self.FG = "#000000"
            self.ENTRY_BG = "#f0f0f0"
            self.ACCENT = "#00adb5"
            self.theme = "light"
            self.toggle_btn.config(text="Switch to Dark Mode")
        else:
            self.BG = "#1e1e1e"
            self.FG = "#ffffff"
            self.ENTRY_BG = "#2c2c2c"
            self.ACCENT = "#00adb5"
            self.theme = "dark"
            self.toggle_btn.config(text="Switch to Light Mode")

        # Refresh all widgets
        self.reload_theme()

    def reload_theme(self):
        self.root.configure(bg=self.BG)

        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=self.BG)
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):
                        child.configure(bg=self.BG, fg=self.FG)
                    elif isinstance(child, tk.Entry):
                        child.configure(bg=self.ENTRY_BG, fg=self.FG, insertbackground=self.FG)
                    elif isinstance(child, tk.Button):
                        if child != self.toggle_btn:
                            child.configure(bg=self.ACCENT, fg="black", activebackground="#00cfd5")

        self.total_label.configure(bg=self.BG, fg=self.FG)
        self.insight_label.configure(bg=self.BG, fg=self.FG)
        for col in self.tree["columns"]:
            self.tree.heading(col, background=self.BG, foreground=self.FG)
        self.tree.configure(background=self.ENTRY_BG, foreground=self.FG)
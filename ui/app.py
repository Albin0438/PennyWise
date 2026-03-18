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
        # ===== Root window =====
        self.root = tk.Tk()
        self.root.title("PennyWise 💰")
        self.root.geometry("800x600")
        self.root.configure(bg=self.BG)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background=self.ENTRY_BG, foreground=self.FG, fieldbackground=self.ENTRY_BG, rowheight=25)
        style.map("Treeview", background=[("selected", self.ACCENT)])

        style.configure("green.Horizontal.TProgressbar", foreground="green", background="green")
        style.configure("yellow.Horizontal.TProgressbar", foreground="orange", background="orange")
        style.configure("red.Horizontal.TProgressbar", foreground="red", background="red")

        # ===== Main Frame =====
        self.main_frame = tk.Frame(self.root, bg=self.BG)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # ===== Top Frame (controls) =====
        top_frame = tk.Frame(self.main_frame, bg=self.BG)
        top_frame.pack(fill="x")

        # Search Frame
        search_frame = tk.Frame(top_frame, bg=self.BG)
        search_frame.pack(side="top", anchor="w", pady=5)
        tk.Label(search_frame, text="Search:", bg=self.BG, fg=self.FG).pack(side="left")
        self.search_entry = tk.Entry(search_frame, bg=self.ENTRY_BG, fg=self.FG, insertbackground=self.FG)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.live_search)
        tk.Button(search_frame, text="Go", command=self.search_data, bg=self.ACCENT, fg="black", relief="flat").pack(side="left")

        # Filter Frame
        categories = ["All", "Food", "Transport", "Shopping", "Other"]
        self.category_var = tk.StringVar(value="All")
        filter_frame = tk.Frame(top_frame, bg=self.BG)
        filter_frame.pack(side="top", anchor="w", pady=5)
        tk.Label(filter_frame, text="Filter Category:", bg=self.BG, fg=self.FG).pack(side="left")
        menu = tk.OptionMenu(filter_frame, self.category_var, *categories, command=lambda e: self.load_data())
        menu.config(bg=self.ENTRY_BG, fg=self.FG, activebackground=self.ACCENT)
        menu["menu"].config(bg=self.ENTRY_BG, fg=self.FG)
        menu.pack(side="left")

        # Buttons Frame
        button_frame = tk.Frame(top_frame, bg=self.BG)
        button_frame.pack(side="top", pady=10)
        self.theme = "dark"
        for text, cmd in [
            ("Add Expense", self.add_expense),
            ("Switch to Light Mode", self.toggle_theme),
            ("Delete Selected", self.delete_selected),
            ("Show Graph 📊", self.show_graph),
            ("Export to CSV 📁", self.export_csv)
        ]:
            btn = tk.Button(button_frame, text=text, command=cmd, bg=self.ACCENT, fg="black", relief="flat")
            btn.pack(side="top", pady=5)
            self.style_button(btn)
            if text == "Switch to Light Mode":
                self.toggle_btn = btn

        # Bar Chart button
        bar_btn = tk.Button(button_frame, text="Bar Chart 📊", command=self.show_bar_chart, bg=self.ACCENT, fg="black", relief="flat")
        bar_btn.pack(side="top", pady=5)
        self.style_button(bar_btn)

        # Pie Chart button
        pie_btn = tk.Button(button_frame, text="Pie Chart 🥧", command=self.show_pie_chart, bg=self.ACCENT, fg="black", relief="flat")
        pie_btn.pack(side="top", pady=5)
        self.style_button(pie_btn)

        # ===== Treeview Frame =====
        tree_frame = tk.Frame(self.main_frame, bg=self.BG)
        tree_frame.pack(fill="both", expand=True, pady=10)

        self.tree = ttk.Treeview(tree_frame, columns=("Title", "Amount", "Category", "Date"), show="headings")
        for col in ("Title", "Amount", "Category", "Date"):
            self.tree.heading(col, text=col)
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # ===== Total + Insight =====
        info_frame = tk.Frame(self.main_frame, bg=self.BG)
        info_frame.pack(pady=10)
        self.total_label = tk.Label(info_frame, text="Total: ₹0", bg=self.BG, fg=self.FG, font=("Arial", 12, "bold"))
        self.total_label.pack()
        self.insight_label = tk.Label(info_frame, text="", bg=self.BG, fg=self.FG, font=("Arial", 12))
        self.insight_label.pack()

        # ===== Budget + Progress =====
        budget_frame = tk.Frame(self.main_frame, bg=self.BG)
        budget_frame.pack(pady=5)
        tk.Label(budget_frame, text="Monthly Budget:", bg=self.BG, fg=self.FG).pack(side="left")
        self.budget_entry = tk.Entry(budget_frame, bg=self.ENTRY_BG, fg=self.FG, insertbackground=self.FG)
        self.budget_entry.pack(side="left", padx=5)
        tk.Button(budget_frame, text="Set", command=self.set_budget, bg=self.ACCENT, fg="black", relief="flat").pack(side="left")

        tk.Label(self.main_frame, text="Budget Usage", bg=self.BG, fg=self.FG).pack()
        self.progress = ttk.Progressbar(self.main_frame, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=5)

        self.load_data()

    # ===== Other methods remain the same =====
    def add_expense(self):
        TransactionForm(self.main_frame, self.load_data)

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

            if not hasattr(self, "budget_warning_shown"):
                self.budget_warning_shown = False

            if percent >= 100 and not self.budget_warning_shown:
                from tkinter import messagebox
                messagebox.showwarning(
                    "Budget Exceeded",
                    f"⚠️ Budget exceeded!\nTotal: ₹{total} / Budget: ₹{self.budget}"
                )
                self.budget_warning_shown = True

            elif percent < 100:
                self.budget_warning_shown = False
        else:
            self.progress["value"] = 0

    def delete_selected(self):
        selected = self.tree.selection()

        if not selected:
            from tkinter import messagebox
            messagebox.showwarning("No selection", "Please select a row")
            return

        item = self.tree.item(selected[0])
        title, amount, category, date = item["values"]

        # Clean amount
        amount = float(str(amount).replace("₹", ""))

        # Convert date back to DB format
        from datetime import datetime
        date = datetime.strptime(date, "%d-%m-%Y").strftime("%Y-%m-%d")

        from core.database import delete_transaction
        delete_transaction(title, amount, category, date)

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
            remaining = self.budget - total if hasattr(self, "budget") else 0

            self.insight_label.config(
                text=f"Top: {top_category} | Remaining: ₹{remaining}"
            )
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
        # Update scrollable frame background
        self.main_frame.configure(bg=self.BG)

        # Update ttk styles
        style = ttk.Style()
        style.theme_use("default")

        # Treeview
        style.configure(
            "Treeview",
            background=self.ENTRY_BG,
            foreground=self.FG,
            fieldbackground=self.ENTRY_BG,
            rowheight=25
        )
        style.configure(
            "Treeview.Heading",
            background=self.BG,
            foreground=self.FG
        )
        style.map(
            "Treeview",
            background=[("selected", self.ACCENT)],
            foreground=[("selected", "black")]
        )

        # Progress bars
        style.configure("green.Horizontal.TProgressbar", foreground="green", background="green")
        style.configure("yellow.Horizontal.TProgressbar", foreground="orange", background="orange")
        style.configure("red.Horizontal.TProgressbar", foreground="red", background="red")

        # Dynamic hover color based on theme
        hover_color = "#00cfd5" if self.theme == "dark" else "#00adb5"

        # Update all children widgets
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=self.BG)
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):
                        child.configure(bg=self.BG, fg=self.FG)
                    elif isinstance(child, tk.Entry):
                        child.configure(bg=self.ENTRY_BG, fg=self.FG, insertbackground=self.FG)
                    elif isinstance(child, tk.Button):
                        if child == self.toggle_btn:
                            continue  # toggle_btn handled separately
                        child.configure(bg=self.ACCENT, fg="black", activebackground=hover_color)
                        # Re-bind hover dynamically
                        child.bind("<Enter>", lambda e, b=child: b.config(bg=hover_color))
                        child.bind("<Leave>", lambda e, b=child: b.config(bg=self.ACCENT))
                    elif isinstance(child, tk.OptionMenu):
                        child.configure(bg=self.ENTRY_BG, fg=self.FG, activebackground=self.ACCENT)
                        child["menu"].config(bg=self.ENTRY_BG, fg=self.FG)

        # Update labels outside frames
        self.total_label.configure(bg=self.BG, fg=self.FG)
        self.insight_label.configure(bg=self.BG, fg=self.FG)

        # Update Treeview again just in case
        self.tree.configure(
            background=self.ENTRY_BG,
            foreground=self.FG,
            fieldbackground=self.ENTRY_BG
        )

    def show_bar_chart(self):
        import matplotlib.pyplot as plt
        from collections import defaultdict

        data = get_transactions()
        category_totals = defaultdict(float)

        for row in data:
            category_totals[row[3]] += row[2]

        if not category_totals:
            return

        categories = list(category_totals.keys())
        amounts = [category_totals[c] for c in categories]

        plt.figure()
        plt.bar(categories, amounts, color='skyblue')
        plt.title("Expenses by Category")
        plt.ylabel("Amount (₹)")
        plt.xlabel("Category")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def show_pie_chart(self):
        import matplotlib.pyplot as plt
        from collections import defaultdict

        data = get_transactions()
        category_totals = defaultdict(float)

        for row in data:
            category_totals[row[3]] += row[2]

        if not category_totals:
            return

        categories = list(category_totals.keys())
        amounts = [category_totals[c] for c in categories]

        plt.figure()
        plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
        plt.title("Expenses Distribution")
        plt.show()
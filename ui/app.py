import tkinter as tk
from tkinter import ttk
from datetime import datetime
from ui.transaction_form import TransactionForm
from core.database import get_transactions
from utils.backup import backup_database
from utils.backup import backup_database, restore_database

from utils.csv_handler import import_csv
from tkinter import filedialog, messagebox

from utils.settings import load_settings, save_settings

class ExpenseApp:
    BG = "#1e1e1e"
    FG = "#ffffff"
    ACCENT = "#00adb5"
    ENTRY_BG = "#2c2c2c"

    def __init__(self):
        
        self.settings = load_settings()

        self.theme = self.settings.get("theme", "dark")

        if self.theme == "light":
            self.BG = "#ffffff"
            self.FG = "#000000"
            self.ENTRY_BG = "#f0f0f0"
            self.ACCENT = "#00adb5"
        else:
            self.BG = "#1e1e1e"
            self.FG = "#ffffff"
            self.ENTRY_BG = "#2c2c2c"
            self.ACCENT = "#00adb5"

        # ===== Root window =====
        self.root = tk.Tk()
        self.root.title("PennyWise 💰")
        self.root.geometry("900x600")
        self.root.configure(bg=self.BG)

        style = ttk.Style()
        style.theme_use("default")

        style.configure("Treeview", background=self.ENTRY_BG, foreground=self.FG,
                        fieldbackground=self.ENTRY_BG, rowheight=25)
        style.map("Treeview", background=[("selected", self.ACCENT)])

        style.configure("green.Horizontal.TProgressbar", background="green")
        style.configure("yellow.Horizontal.TProgressbar", background="orange")
        style.configure("red.Horizontal.TProgressbar", background="red")

        # ===== Main Layout =====
        self.main_frame = tk.Frame(self.root, bg=self.BG)
        self.main_frame.pack(fill="both", expand=True)

        # Sidebar (LEFT)
        self.sidebar = tk.Frame(self.main_frame, bg=self.BG, width=200)
        self.sidebar.pack(side="left", fill="y")

        # Content (RIGHT)
        self.content = tk.Frame(self.main_frame, bg=self.BG)
        self.content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # ===== TOP (Search + Filter) =====
        top_frame = tk.Frame(self.content, bg=self.BG)
        top_frame.pack(fill="x")

        # Search
        search_frame = tk.Frame(top_frame, bg=self.BG)
        search_frame.pack(anchor="w", pady=5)

        tk.Label(search_frame, text="Search:", bg=self.BG, fg=self.FG).pack(side="left")
        self.search_entry = tk.Entry(search_frame, bg=self.ENTRY_BG, fg=self.FG, insertbackground=self.FG)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.live_search)

        tk.Button(search_frame, text="Go", command=self.search_data,
                bg=self.ACCENT, fg="black").pack(side="left")

        # Filter
        filter_frame = tk.Frame(top_frame, bg=self.BG)
        filter_frame.pack(anchor="w", pady=5)

        categories = ["All", "Food", "Transport", "Shopping", "Other"]
        self.category_var = tk.StringVar(value="All")

        tk.Label(filter_frame, text="Filter Category:", bg=self.BG, fg=self.FG).pack(side="left")

        menu = tk.OptionMenu(filter_frame, self.category_var, *categories,
                            command=lambda e: self.load_data())
        menu.config(bg=self.ENTRY_BG, fg=self.FG)
        menu["menu"].config(bg=self.ENTRY_BG, fg=self.FG)
        menu.pack(side="left")

        # ===== DATE FILTER =====
        date_filter_frame = tk.Frame(top_frame, bg=self.BG)
        date_filter_frame.pack(anchor="w", pady=5)

        # Year
        self.year_var = tk.StringVar(value="All")
        years = ["All"] + [str(y) for y in range(2020, datetime.now().year + 1)]

        tk.Label(date_filter_frame, text="Year:", bg=self.BG, fg=self.FG).pack(side="left")
        year_menu = tk.OptionMenu(date_filter_frame, self.year_var, *years,
                                command=lambda e: self.load_data())
        year_menu.config(bg=self.ENTRY_BG, fg=self.FG)
        year_menu["menu"].config(bg=self.ENTRY_BG, fg=self.FG)
        year_menu.pack(side="left", padx=5)

        # Month
        self.month_var = tk.StringVar(value="All")
        months = ["All"] + [f"{i:02d}" for i in range(1, 13)]

        tk.Label(date_filter_frame, text="Month:", bg=self.BG, fg=self.FG).pack(side="left")
        month_menu = tk.OptionMenu(date_filter_frame, self.month_var, *months,
                                command=lambda e: self.load_data())
        month_menu.config(bg=self.ENTRY_BG, fg=self.FG)
        month_menu["menu"].config(bg=self.ENTRY_BG, fg=self.FG)
        month_menu.pack(side="left", padx=5)

        # Day
        self.day_var = tk.StringVar(value="All")
        days = ["All"] + [f"{i:02d}" for i in range(1, 32)]

        tk.Label(date_filter_frame, text="Day:", bg=self.BG, fg=self.FG).pack(side="left")
        day_menu = tk.OptionMenu(date_filter_frame, self.day_var, *days,
                                command=lambda e: self.load_data())
        day_menu.config(bg=self.ENTRY_BG, fg=self.FG)
        day_menu["menu"].config(bg=self.ENTRY_BG, fg=self.FG)
        day_menu.pack(side="left", padx=5)

        # --- Data ---
        tk.Label(self.sidebar, text="Data", bg=self.BG, fg=self.FG).pack(pady=5)

        for text, cmd in [
            ("Add Expense", self.add_expense),
            ("Delete Selected", self.delete_selected),
        ]:
            btn = tk.Button(self.sidebar, text=text, command=cmd, bg=self.ACCENT)
            btn.pack(fill="x", padx=10, pady=2)
            self.style_button(btn)

        # --- Analytics ---
        tk.Label(self.sidebar, text="Analytics", bg=self.BG, fg=self.FG).pack(pady=10)

        for text, cmd in [
            ("Line Graph 📊", self.show_graph),
            ("Bar Chart 📊", self.show_bar_chart),
            ("Pie Chart 🥧", self.show_pie_chart),
            ("Timeline 📈", self.show_timeline_chart),
        ]:
            btn = tk.Button(self.sidebar, text=text, command=cmd, bg=self.ACCENT)
            btn.pack(fill="x", padx=10, pady=2)
            self.style_button(btn)

        # --- Data Management ---
        tk.Label(self.sidebar, text="Data Management", bg=self.BG, fg=self.FG).pack(pady=10)

        for text, cmd in [
            ("Import Data (CSV)", self.import_csv_ui),   # ✅ ADD THIS LINE
            ("Export CSV", self.export_csv),
            ("Backup", backup_database),
            ("Restore", restore_database),
        ]:
            btn = tk.Button(self.sidebar, text=text, command=cmd, bg=self.ACCENT)
            btn.pack(fill="x", padx=10, pady=2)
            self.style_button(btn)

        # --- Settings ---
        tk.Label(self.sidebar, text="Settings", bg=self.BG, fg=self.FG).pack(pady=10)

        self.toggle_btn = tk.Button(self.sidebar, text="Toggle Theme",
                                    command=self.toggle_theme, bg=self.ACCENT)
        self.toggle_btn.pack(fill="x", padx=10, pady=2)
        self.style_button(self.toggle_btn)

        # ===== TABLE =====
        tree_frame = tk.Frame(self.content, bg=self.BG)
        tree_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(tree_frame,
                                columns=("Title", "Amount", "Category", "Date"),
                                show="headings")

        for col in ("Title", "Amount", "Category", "Date"):
            self.tree.heading(col, text=col)

        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(tree_frame, command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # ===== INFO =====
        info_frame = tk.Frame(self.content, bg=self.BG)
        info_frame.pack(pady=5)

        self.total_label = tk.Label(info_frame, text="Total: ₹0",
                                    bg=self.BG, fg=self.FG, font=("Arial", 12, "bold"))
        self.total_label.pack()

        self.insight_label = tk.Label(info_frame, text="",
                                    bg=self.BG, fg=self.FG)
        self.insight_label.pack()

        # ===== BUDGET =====
        budget_frame = tk.Frame(self.content, bg=self.BG)
        budget_frame.pack(pady=5)

        tk.Label(budget_frame, text="Monthly Budget:",
                bg=self.BG, fg=self.FG).pack(side="left")

        self.budget_entry = tk.Entry(budget_frame,
                                    bg=self.ENTRY_BG, fg=self.FG,
                                    insertbackground=self.FG)
        self.budget_entry.pack(side="left", padx=5)

        self.budget = self.settings.get("budget", 0)
        self.budget_entry.insert(0, str(self.budget))

        tk.Button(budget_frame, text="Set",
                command=self.set_budget, bg=self.ACCENT).pack(side="left")

        tk.Label(self.content, text="Budget Usage",
                bg=self.BG, fg=self.FG).pack()

        self.progress = ttk.Progressbar(self.content,
                                    orient="horizontal",
                                    length=300,
                                    mode="determinate")
        self.progress.pack(pady=5)

        tk.Label(self.content,
                text="⚠️ After restoring backup, restart the app",
                bg=self.BG, fg="orange").pack()

        self.load_data()

        try:
            self.reload_theme()
        except Exception as e:
            print("Theme error:", e)

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

        category_filter = self.category_var.get()

        # ===== FILTERED DATA (IMPORTANT) =====
        filtered_data = []

        for row in data:
            date_str = row[4]  # "YYYY-MM-DD"
            year, month, day = date_str.split("-")

            # Date filters
            if hasattr(self, "year_var") and self.year_var.get() != "All" and self.year_var.get() != year:
                continue

            if hasattr(self, "month_var") and self.month_var.get() != "All" and self.month_var.get() != month:
                continue

            if hasattr(self, "day_var") and self.day_var.get() != "All" and self.day_var.get() != day:
                continue

            # Category filter
            if category_filter != "All" and row[3] != category_filter:
                continue

            filtered_data.append(row)

        # ===== CATEGORY TOTALS (based on filtered data) =====
        category_totals = {}
        for row in filtered_data:
            category_totals[row[3]] = category_totals.get(row[3], 0) + row[2]

        if category_totals:
            top_category = max(category_totals, key=category_totals.get)
            self.insight_label.config(
                text=f"Top spending category: {top_category} (₹{category_totals[top_category]})"
            )
        else:
            self.insight_label.config(text="")

        # ===== INSERT INTO TABLE =====
        for row in filtered_data:
            formatted_date = datetime.strptime(row[4], "%Y-%m-%d").strftime("%d-%m-%Y")

            self.tree.insert(
                "",
                "end",
                values=(row[1], f"₹{row[2]}", row[3], formatted_date)
            )

            total += row[2]

        self.total_label.config(text=f"Total: ₹{total}")

        # ===== BUDGET LOGIC =====
        if hasattr(self, "budget") and self.budget > 0:
            percent = (total / self.budget) * 100
            self.progress["value"] = percent

            if percent < 70:
                self.progress.configure(style="green.Horizontal.TProgressbar")
            elif percent < 100:
                self.progress.configure(style="yellow.Horizontal.TProgressbar")
            else:
                self.progress.configure(style="red.Horizontal.TProgressbar")

            if not hasattr(self, "budget_warning_shown"):
                self.budget_warning_shown = False

            if percent >= 100 and not self.budget_warning_shown:
                messagebox.showwarning(
                    "Budget Exceeded",
                    f"⚠️ Budget exceeded!\nTotal: ₹{total} / Budget: ₹{self.budget}"
                )

                self.shake_window()   # 🌋 ADD THIS

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

        item_id = selected[0]

        # 👉 Get index BEFORE deleting
        index = self.tree.index(item_id)

        item = self.tree.item(item_id)
        title, amount, category, date = item["values"]

        # Clean amount
        amount = float(str(amount).replace("₹", ""))

        # Convert date back to DB format
        from datetime import datetime
        date = datetime.strptime(date, "%d-%m-%Y").strftime("%Y-%m-%d")

        from core.database import delete_transaction
        delete_transaction(title, amount, category, date)

        # Reload data
        self.load_data()

        # 👉 Get all items after reload
        items = self.tree.get_children()

        if not items:
            return

        # 👉 Select next item (or previous if last was deleted)
        if index < len(items):
            next_item = items[index]
        else:
            next_item = items[-1]

        self.tree.selection_set(next_item)
        self.tree.focus(next_item)
        self.tree.see(next_item)

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

            self.settings["budget"] = self.budget
            save_settings(self.settings)

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
            self.theme = "dark"   # ✅ ADD THIS LINE
            self.toggle_btn.config(text="Switch to Light Mode")

        self.reload_theme()
        self.root.update_idletasks()

        self.settings["theme"] = self.theme
        save_settings(self.settings)

    def apply_theme_recursive(self, widget):
        try:
            if isinstance(widget, tk.Frame):
                widget.configure(bg=self.BG)

            elif isinstance(widget, tk.Label):
                widget.configure(bg=self.BG, fg=self.FG)

            elif isinstance(widget, tk.Entry):
                widget.configure(bg=self.ENTRY_BG, fg=self.FG, insertbackground=self.FG)

            elif isinstance(widget, tk.Button):
                if widget == self.toggle_btn:
                    return
                hover_color = "#00cfd5" if self.theme == "dark" else "#00adb5"
                widget.configure(bg=self.ACCENT, fg="black", activebackground=hover_color)
                widget.bind("<Enter>", lambda e, b=widget: b.config(bg=hover_color))
                widget.bind("<Leave>", lambda e, b=widget: b.config(bg=self.ACCENT))

            elif isinstance(widget, tk.OptionMenu):
                widget.configure(bg=self.ENTRY_BG, fg=self.FG, activebackground=self.ACCENT)
                widget["menu"].config(bg=self.ENTRY_BG, fg=self.FG)

            elif isinstance(widget, tk.Scrollbar):
                widget.configure(bg=self.BG)

        except:
            pass

        # 🔁 RECURSION (this is the magic)
        for child in widget.winfo_children():
            self.apply_theme_recursive(child)

    def reload_theme(self):
        # ✅ Root + main backgrounds (fixes edges issue)
        self.root.configure(bg=self.BG)
        self.main_frame.configure(bg=self.BG)

        # ===== ttk styles =====
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

        # ✅ Fix Progressbar (IMPORTANT)
        style.configure(
            "Horizontal.TProgressbar",
            troughcolor=self.ENTRY_BG,
            background="green"
        )

        style.configure("green.Horizontal.TProgressbar", background="green")
        style.configure("yellow.Horizontal.TProgressbar", background="orange")
        style.configure("red.Horizontal.TProgressbar", background="red")

        # ===== Apply theme to ALL widgets (recursive) =====
        self.apply_theme_recursive(self.root)

        # ===== Fix Treeview container explicitly =====
        self.tree.master.configure(bg=self.BG)

        # ===== Ensure labels update =====
        self.total_label.configure(bg=self.BG, fg=self.FG)
        self.insight_label.configure(bg=self.BG, fg=self.FG)

        # ===== Ensure Treeview refresh =====
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

    def show_timeline_chart(self):
        import matplotlib.pyplot as plt
        from collections import defaultdict
        from datetime import datetime

        data = get_transactions()

        # Safety check
        if not data:
            from tkinter import messagebox
            messagebox.showinfo("No Data", "No transactions to display")
            return

        # Aggregate daily totals
        daily_totals = defaultdict(float)

        for row in data:
            date_str = row[4]
            amount = row[2]

            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            daily_totals[date_obj] += amount

        # Sort dates
        dates = sorted(daily_totals.keys())
        amounts = [daily_totals[d] for d in dates]

        # Convert to readable labels
        labels = [d.strftime("%d-%m") for d in dates]

        # Plot
        plt.figure()
        plt.plot(labels, amounts, marker='o')

        plt.title("Expense Timeline")
        plt.xlabel("Date")
        plt.ylabel("Amount (₹)")

        plt.xticks(rotation=45)
        plt.grid()
        plt.tight_layout()

        plt.show()

    def restore_database(self):
        import shutil
        from tkinter import filedialog, messagebox

        db_file = "pennywise.db"

        file_path = filedialog.askopenfilename(
            filetypes=[("Database Files", "*.db")],
            title="Select Backup File"
        )

        if not file_path:
            return

        try:
            shutil.copy(file_path, db_file)
            messagebox.showinfo(
                "Success",
                "Database restored!\n⚠️ Please restart the app."
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def import_csv_ui(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv")]
        )

        if file_path:
            try:
                inserted, skipped = import_csv(file_path)

                messagebox.showinfo(
                    "Import Complete",
                    f"Inserted: {inserted}\nSkipped (duplicates): {skipped}"
                )
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def shake_window(self):
        x = self.root.winfo_x()
        y = self.root.winfo_y()

        for _ in range(10):  # number of shakes
            self.root.geometry(f"+{x + 10}+{y}")
            self.root.update()
            self.root.after(20)

            self.root.geometry(f"+{x - 10}+{y}")
            self.root.update()
            self.root.after(20)

        self.root.geometry(f"+{x}+{y}")
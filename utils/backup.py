import shutil
import os
from tkinter import filedialog, messagebox

DB_FILE = "expenses.db"


def backup_database():
    # Ask user where to save
    file_path = filedialog.asksaveasfilename(
        title="Save Backup",
        defaultextension=".db",
        filetypes=[("Database Files", "*.db"), ("All Files", "*.*")]
    )

    if not file_path:
        return  # user cancelled

    try:
        shutil.copy(DB_FILE, file_path)
        messagebox.showinfo("Success", f"Backup saved to:\n{file_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def restore_database():
    # Ask user to pick backup file
    file_path = filedialog.askopenfilename(
        title="Select Backup File",
        filetypes=[("Database Files", "*.db"), ("All Files", "*.*")]
    )

    if not file_path:
        return  # user cancelled

    try:
        shutil.copy(file_path, DB_FILE)
        messagebox.showinfo(
            "Restored",
            "Database restored successfully!\nPlease restart the app."
        )
    except Exception as e:
        messagebox.showerror("Error", str(e))
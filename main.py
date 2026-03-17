from core.database import init_db
from ui.app import ExpenseApp

if __name__ == "__main__":
    init_db()

    app = ExpenseApp()
    app.run()
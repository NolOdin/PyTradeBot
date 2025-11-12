# data_manager.py
import sqlite3
import pandas as pd
from datetime import datetime
from config import DB_PATH

class DataManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.init_db()

    def init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                action TEXT,
                price REAL,
                amount REAL,
                profit_loss REAL,
                signal_strength REAL
            )
        ''')
        self.conn.commit()

    def save_trade(self, action, price, amount, signal_strength=0.5):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO trades (timestamp, action, price, amount, profit_loss, signal_strength)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), action, price, amount, 0.0, signal_strength))
        self.conn.commit()

    def get_history(self, limit=100):
        return pd.read_sql_query(
            "SELECT * FROM trades ORDER BY timestamp DESC LIMIT ?",
            self.conn, params=(limit,)
        )

    def update_profit_loss(self, trade_id, profit_loss):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE trades SET profit_loss = ? WHERE id = ?", (profit_loss, trade_id))
        self.conn.commit()

    def close(self):
        self.conn.close()
    def export_csv(self, path='trades_report.csv'):
        df = self.get_history(1000)
        df.to_csv(path, index=False)
        print(f"Отчёт сохранён: {path}")

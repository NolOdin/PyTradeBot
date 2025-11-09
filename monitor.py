# monitor.py
import logging
from datetime import datetime

logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Monitor:
    @staticmethod
    def log_trade(action, price, profit_loss=0):
        logging.info(f"Trade: {action} at {price}, P/L: {profit_loss}")

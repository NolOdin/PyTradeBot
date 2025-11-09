# trade_engine.py
import ccxt
import time
import json
from config import (
    BYBIT_API_KEY, BYBIT_SECRET, SYMBOL, AMOUNT_ETH,
    STOP_LOSS_PCT, TAKE_PROFIT_PCT, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
)
from ai_predictor import AIPredictor
from data_manager import DataManager
from ml_learner import MLLearner

class TradeEngine:
    def __init__(self):
        self.exchange = ccxt.bybit({
            'apiKey': BYBIT_API_KEY,
            'secret': BYBIT_SECRET,
            'enableRateLimit': True,
            'sandbox': True,
        })
        self.ai = AIPredictor()
        self.dm = DataManager()
        self.ml = MLLearner()
        self.position = None
        self.load_best_params()

    def load_best_params(self):
        try:
            with open('best_params.json', 'r') as f:
                best = json.load(f)
                self.stop_loss = best.get('stop_loss', STOP_LOSS_PCT)
                self.take_profit = best.get('take_profit', TAKE_PROFIT_PCT)
                self.ai_threshold = best.get('ai_threshold', 0.7)
        except:
            self.stop_loss = STOP_LOSS_PCT
            self.take_profit = TAKE_PROFIT_PCT
            self.ai_threshold = 0.7

    def get_market_data(self):
        ticker = self.exchange.fetch_ticker(SYMBOL)
        return ticker['last'], ticker['quoteVolume']

    def execute_trade(self, signal, strength, price):
        if strength < self.ai_threshold:
            return
        amount = AMOUNT_ETH
        if signal == 'BUY' and not self.position:
            order = self.exchange.create_market_buy_order(SYMBOL, amount)
            self.position = {'price': price, 'amount': amount}
            self.dm.save_trade('buy', price, amount, strength)
            self.send_alert(f"BUY {SYMBOL} at {price:.2f}")
        elif signal == 'SELL' and self.position:
            order = self.exchange.create_market_sell_order(SYMBOL, self.position['amount'])
            profit_loss = (price - self.position['price']) / self.position['price'] * 100
            last_id = self.dm.get_history(1)['id'].iloc[0]
            self.dm.update_profit_loss(last_id, profit_loss)
            self.position = None
            self.dm.save_trade('sell', price, amount, strength)
            self.send_alert(f"SELL {SYMBOL} at {price:.2f} | P/L: {profit_loss:+.2f}%")

    def check_stop_loss_take_profit(self, price):
        if not self.position: return
        pct = (price - self.position['price']) / self.position['price']
        if pct <= -self.stop_loss:
            self.execute_trade('SELL', 1.0, price)
        elif pct >= self.take_profit:
            self.execute_trade('SELL', 1.0, price)

    def run_cycle(self):
        price, volume = self.get_market_data()
        history = self.dm.get_history(20)
        signal, strength = self.ai.get_signal(price, volume, history)
        self.check_stop_loss_take_profit(price)
        self.execute_trade(signal, strength, price)
        time.sleep(60)

    def send_alert(self, message):
        print(f"[ALERT] {message}")
        if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
            try:
                from telegram import Bot
                Bot(token=TELEGRAM_TOKEN).send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
            except:
                pass

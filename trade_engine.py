# trade_engine.py
import ccxt
import time
import json
from config import (
    BYBIT_API_KEY, BYBIT_SECRET, SYMBOL,
    STOP_LOSS_PCT, TAKE_PROFIT_PCT, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, START_CAPITAL, RISK_PER_TRADE, MIN_TRADE_USDT
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
            'options': {
                'adjustForTimeDifference': True,
                'recvWindow': 10000,           # ← Увеличено
                'defaultType': 'spot'
            }
        })
        self.ai = AIPredictor()
        self.dm = DataManager()
        self.ml = MLLearner()
        self.position = None
        self.capital = START_CAPITAL   # ← Новый счётчик
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

    def calculate_position_size(self, price):
        """Расчёт размера позиции: 1% риска"""
        risk_amount = self.capital * RISK_PER_TRADE
        stop_price = price * (1 - self.stop_loss)
        if stop_price >= price:
            return 0
        eth_amount = risk_amount / (price - stop_price)
        eth_amount = round(max(eth_amount, 0.001), 3)  # минимум 0.001 ETH

        usdt_value = eth_amount * price
        if usdt_value < MIN_TRADE_USDT or usdt_value > self.capital * 0.95:
            return 0

        return eth_amount

    def execute_buy(self, price, strength):
        amount = self.calculate_position_size(price)
        if amount <= 0:
            print(f"[SKIP] Недостаточно капитала или малая сделка")
            return

        try:
            order = self.exchange.create_market_buy_order(SYMBOL, amount)
            self.position = {'price': price, 'amount': amount}
            self.capital -= amount * price * 1.001  # комиссия 0.1%
            self.dm.save_trade('buy', price, amount, strength)
            self.send_alert(f"BUY {amount:.3f} ETH @ {price:.2f} | Risk: 1%")
            print(f"*** BUY {amount:.3f} ETH @ {price:.2f} | Capital: ${self.capital:.1f} ***")
        except Exception as e:
            print(f"[BUY ERROR] {e}")

    def execute_sell(self, price, strength):
        if not self.position:
            return

        try:
            order = self.exchange.create_market_sell_order(SYMBOL, self.position['amount'])
            proceeds = self.position['amount'] * price * 0.999  # комиссия
            profit_usdt = proceeds - (self.position['amount'] * self.position['price'])
            pl_pct = profit_usdt / (self.position['amount'] * self.position['price']) * 100

            self.capital += proceeds
            last_id = self.dm.get_history(1)['id'].iloc[0]
            self.dm.update_profit_loss(last_id, pl_pct)
            self.dm.save_trade('sell', price, self.position['amount'], strength)

            self.send_alert(
                f"SELL {self.position['amount']:.3f} ETH @ {price:.2f} | "
                f"P/L: {pl_pct:+.2f}% | Capital: ${self.capital:.1f}"
            )
            print(f"*** SELL {self.position['amount']:.3f} ETH @ {price:.2f} | P/L: {pl_pct:+.2f}% ***")
            self.position = None
        except Exception as e:
            print(f"[SELL ERROR] {e}")

    def check_stop_loss_take_profit(self, price):
        if not self.position:
            return
        pct = (price - self.position['price']) / self.position['price']
        if pct <= -self.stop_loss:
            print(f"[STOP-LOSS] {pct*100:+.2f}%")
            self.execute_sell(price, 1.0)
        elif pct >= self.take_profit:
            print(f"[TAKE-PROFIT] {pct*100:+.2f}%")
            self.execute_sell(price, 1.0)

    def run_cycle(self):
        price, volume = self.get_market_data()
        print(f"\n[MARKET] {price:.2f} | Vol: {volume:,.0f}")

        history = self.dm.get_history(20)
        signal, strength = self.ai.get_signal(price, volume, history)
        print(f"[AI] {signal} | Strength: {strength:.2f}")

        self.check_stop_loss_take_profit(price)

        if signal == 'BUY' and not self.position and strength >= self.ai_threshold:
            self.execute_buy(price, strength)
        elif signal == 'SELL' and self.position and strength >= self.ai_threshold:
            self.execute_sell(price, strength)

        print(f"[CAPITAL] ${self.capital:.1f}")
        time.sleep(80)

    def send_alert(self, message):
        print(f"[ALERT] {message}")
        if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
            try:
                from telegram import Bot
                Bot(token=TELEGRAM_TOKEN).send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
            except:
                pass
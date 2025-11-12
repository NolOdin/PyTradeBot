# backtest.py
import ccxt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from trade_engine import TradeEngine
from data_manager import DataManager
from config import SYMBOL, STOP_LOSS_PCT, TAKE_PROFIT_PCT, START_CAPITAL
from monitor import Monitor

class Backtester:
    def __init__(self, days=60, timeframe='1h', slippage=0.0005, commission=0.001):
        self.exchange = ccxt.bybit({'enableRateLimit': True})
        self.symbol = SYMBOL
        self.timeframe = timeframe
        self.slippage = slippage
        self.commission = commission
        self.dm = DataManager()
        self.engine = TradeEngine()
        self.engine.exchange = self.exchange

    def fetch_data(self, days):
        since = self.exchange.parse8601(
            (pd.Timestamp.now() - pd.Timedelta(days=days + 30)).isoformat()
        )
        raw = self.exchange.fetch_ohlcv(self.symbol, self.timeframe, since)
        df = pd.DataFrame(raw, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df[df['timestamp'] >= (pd.Timestamp.now() - pd.Timedelta(days=days))]
        return df.set_index('timestamp')

    def apply_slippage_and_commission(self, price, side):
        if side == 'buy':
            return price * (1 + self.slippage + self.commission)
        else:
            return price * (1 - self.slippage - self.commission)

    def run(self, plot=True):
        df = self.fetch_data(days=60)
        capital = START_CAPITAL
        position = 0.0
        entry_price = 0.0
        equity_curve = []
        trades = []

        for i, (ts, row) in enumerate(df.iterrows()):
            price = row['close']
            volume = row['volume']
            signal, strength = self.engine.ai.get_signal(price, volume, pd.DataFrame())

            if position > 0:
                pct = (price - entry_price) / entry_price
                if pct <= -STOP_LOSS_PCT or pct >= TAKE_PROFIT_PCT:
                    signal, strength = 'SELL', 1.0

            if signal == 'BUY' and strength >= 0.7 and position == 0:
                buy_price = self.apply_slippage_and_commission(price, 'buy')
                position = (capital * 0.95) / buy_price
                entry_price = buy_price
                capital *= 0.05
                trades.append({'time': ts, 'action': 'buy', 'price': buy_price})

            elif signal == 'SELL' and position > 0:
                sell_price = self.apply_slippage_and_commission(price, 'sell')
                proceeds = position * sell_price
                capital += proceeds
                profit = proceeds - (position * entry_price)
                trades.append({'time': ts, 'action': 'sell', 'price': sell_price, 'profit': profit})
                position = 0

            total = capital + (position * price if position else 0)
            equity_curve.append({'time': ts, 'equity': total})

        equity_df = pd.DataFrame(equity_curve).set_index('time')
        returns = equity_df['equity'].pct_change().dropna()
        total_return = (equity_df['equity'].iloc[-1] / 1000 - 1) * 100
        max_drawdown = ((equity_df['equity'].cummax() - equity_df['equity']) / equity_df['equity'].cummax()).max() * 100
        sharpe = returns.mean() / returns.std() * np.sqrt(24 * 365 / 24) if returns.std() != 0 else 0

        print(f"Доходность: {total_return:+.2f}% | Max DD: {max_drawdown:.2f}% | Sharpe: {sharpe:.2f}")

        if plot:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
            ax1.plot(df.index, df['close'], label='ETH/USDT')
            ax1.scatter([t['time'] for t in trades if t['action']=='buy'], df.loc[[t['time'] for t in trades if t['action']=='buy']]['close'], color='green', marker='^', s=80)
            ax1.scatter([t['time'] for t in trades if t['action']=='sell'], df.loc[[t['time'] for t in trades if t['action']=='sell']]['close'], color='red', marker='v', s=80)
            ax1.legend()
            ax2.plot(equity_df.index, equity_df['equity'], color='blue')
            ax2.fill_between(equity_df.index, equity_df['equity'], 1000, alpha=0.2)
            plt.show()

        return equity_df

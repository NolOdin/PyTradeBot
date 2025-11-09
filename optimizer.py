# optimizer.py
import json
import itertools
import pandas as pd
import numpy as np
from backtest import Backtester
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

class StrategyOptimizer:
    def __init__(self):
        self.bt = Backtester()

    def objective(self, params):
        # Упрощённая версия для оптимизации
        return np.random.uniform(0.5, 2.0)  # ← Замени на реальный бэктест

    def run_grid_search(self):
        param_grid = {
            'stop_loss': [0.01, 0.02, 0.03],
            'take_profit': [0.03, 0.05, 0.08],
            'ai_threshold': [0.6, 0.7, 0.8]
        }

        best_sharpe = -np.inf
        best_params = None

        for params in itertools.product(*param_grid.values()):
            p = dict(zip(param_grid.keys(), params))
            sharpe = self.objective(p)
            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_params = p

        with open('best_params.json', 'w') as f:
            json.dump(best_params, f, indent=2)

        print("Лучшие параметры:", best_params)

        # === ОПЦИОНАЛЬНЫЙ TELEGRAM ===
        if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
            try:
                from telegram import Bot
                msg = f"*Оптимизация*\nSL: `{best_params['stop_loss']}`\nTP: `{best_params['take_profit']}`"
                Bot(token=TELEGRAM_TOKEN).send_message(chat_id=TELEGRAM_CHAT_ID, text=msg, parse_mode='Markdown')
            except:
                pass

        return best_params

# config.py
import os

# === ОБЯЗАТЕЛЬНО ===
BYBIT_API_KEY = os.getenv('BYBIT_API_KEY', 'your_bybit_api_key')
BYBIT_SECRET = os.getenv('BYBIT_SECRET', 'your_bybit_secret')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'your_deepseek_key')
DEEPSEEK_BASE_URL = 'https://api.deepseek.com/v1'

# === ТОРГОВЛЯ ===
SYMBOL = 'ETH/USDT'
AMOUNT_ETH = 0.01
STOP_LOSS_PCT = 0.02
TAKE_PROFIT_PCT = 0.05
DB_PATH = 'trades.db'

# === ТЕЛЕГРАМ — ОПЦИОНАЛЬНО ===
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')        # None = отключено
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')    # None = отключено
# config.py (добавь в конец)
# === OPENROUTER (для DeepSeek R1 и других) ===
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')  # None = используем DeepSeek
OPENROUTER_BASE_URL = 'https://openrouter.ai/api/v1'
DEEPSEEK_R1_MODEL = 'deepseek/deepseek-r1:free'  # :free = бесплатно, или :nitro для скорости

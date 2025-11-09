# ai_predictor.py
import requests
import json
from config import (
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL,
    OPENROUTER_API_KEY, OPENROUTER_BASE_URL, DEEPSEEK_R1_MODEL
)

class AIPredictor:
    def __init__(self):
        self.model = DEEPSEEK_R1_MODEL if OPENROUTER_API_KEY else "deepseek-chat"
        self.base_url = OPENROUTER_BASE_URL if OPENROUTER_API_KEY else DEEPSEEK_BASE_URL
        self.api_key = OPENROUTER_API_KEY if OPENROUTER_API_KEY else DEEPSEEK_API_KEY

    def get_signal(self, current_price, volume, history_data):
        prompt = f"""
        Analyze ETH/USDT: price {current_price}, volume {volume}.
        History: {history_data.tail(5).to_json() if not history_data.empty else 'No data'}.
        Respond ONLY with JSON: {{"signal": "BUY|SELL|HOLD", "strength": 0.0-1.0, "reason": "brief"}}.
        """

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 150,
            "temperature": 0.3
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://your-bot.com",  # Опционально: для лидербордов OpenRouter
            "X-Title": "ETH Trading Bot"  # Опционально
        }

        try:
            response = requests.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            content = response.json()['choices'][0]['message']['content']
            signal_data = json.loads(content)
            return signal_data['signal'], signal_data['strength']
        except Exception as e:
            print(f"[AI Error] {e}. Fallback to HOLD.")
            return "HOLD", 0.5

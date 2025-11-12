# ai_predictor.py
import requests
import json
import time
import re
from config import DEEPSEEK_API_KEY, OPENROUTER_API_KEY

class AIPredictor:
    def __init__(self):
        self.cooldown = 0
        self.prefer_deepseek = bool(DEEPSEEK_API_KEY)
        self.use_openrouter = bool(OPENROUTER_API_KEY)
        if self.prefer_deepseek:
            print("[AI] Основной: DeepSeek")
        elif self.use_openrouter:
            print("[AI] Основной: OpenRouter")
        else:
            print("[AI] Основной: ЛОКАЛЬНАЯ модель (Gemma2:2b)")

    def get_signal(self, current_price, volume, history_data):
        if time.time() < self.cooldown:
            print(f"[AI COOLDOWN] Ждём {int(self.cooldown - time.time())} сек")
            return "HOLD", 0.5

        # Формируем последние 5 свечей
        history_str = (
            history_data.tail(5).to_string(index=False)
            if not history_data.empty and len(history_data) > 0
            else "No history"
        )

        # Жёсткий промпт — Gemma2:2b понимает его идеально
        prompt = f"""
You are a professional crypto analyst. Analyze ETH/USDT using ONLY the provided data.

LIVE DATA:
- Price: {current_price:.2f} USDT
- Volume: {volume:,.0f}
- Last 5 trades:\n{history_str}

INSTRUCTIONS:
1. Detect trend: rising, falling, flat.
2. Volume: spike, normal, low.
3. Signal: BUY (if rising + high volume), SELL (if falling + high volume), HOLD (otherwise).
4. Strength: 0.6–1.0 for strong signal, 0.5 for HOLD.

RETURN ONLY JSON:
{{"signal": "BUY|SELL|HOLD", "strength": 0.5-1.0, "reason": "max 25 chars"}}
"""

        # Приоритет: DeepSeek → OpenRouter → Gemma2:2b
        if self.prefer_deepseek:
            result = self._query_deepseek(prompt)
            if result:
                return result

        if self.use_openrouter:
            result = self._query_openrouter(prompt)
            if result:
                return result

        result = self._query_ollama(prompt)
        if result:
            return result

        print("[AI] Все провайдеры недоступны → HOLD")
        return "HOLD", 0.5

    def _query_deepseek(self, prompt):
        if not DEEPSEEK_API_KEY:
            return None
        try:
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 150,
                    "temperature": 0.3
                },
                headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
                timeout=15
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return self._parse_response(content, "DeepSeek")
        except Exception as e:
            print(f"[DeepSeek Error] {e}")
            return None

    def _query_openrouter(self, prompt):
        if not OPENROUTER_API_KEY:
            return None
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json={
                    "model": "google/gemma-2-9b-it:free",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 100,
                    "temperature": 0.3
                },
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "HTTP-Referer": "https://eth-bot.local",
                    "X-Title": "ETH Bot"
                },
                timeout=20
            )
            if response.status_code == 429:
                self.cooldown = time.time() + 300
                print("[OpenRouter 429] Ждём 5 мин")
                return "HOLD", 0.5
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return self._parse_response(content, "OpenRouter")
        except Exception as e:
            print(f"[OpenRouter Error] {e}")
            return None

    def _query_ollama(self, prompt):
        try:
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "gemma2:2b",  # ← ТВОЯ МОДЕЛЬ
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 150,
                        "num_ctx": 2048
                    }
                },
                timeout=60
            )
            response.raise_for_status()
            content = response.json()["message"]["content"].strip()
            return self._parse_response(content, "Gemma2")

        except requests.exceptions.Timeout:
            print("[Gemma2] Таймаут! Модель думает слишком долго.")
            return "HOLD", 0.5
        except requests.exceptions.ConnectionError:
            print("[Gemma2] Ollama не запущен! Запусти: ollama serve")
            return None
        except Exception as e:
            print(f"[Gemma2 Error] {e}")
            return None

    def _parse_response(self, content, provider):
        print(f"[{provider} RAW] {content[:150]}...")  # Отладка

        # Извлекаем JSON из ```json```
        if "```json" in content:
            try:
                start = content.find("```json") + 7
                end = content.find("```", start)
                if end == -1:
                    end = len(content)
                content = content[start:end].strip()
            except:
                pass

        # Пытаемся распарсить JSON
        try:
            data = json.loads(content)
            signal = data.get("signal", "HOLD").upper()
            if signal not in {"BUY", "SELL", "HOLD"}:
                signal = "HOLD"
            strength = max(0.5, min(1.0, float(data.get("strength", 0.5))))
            reason = str(data.get("reason", "no reason"))[:25]
            print(f"[{provider}] {signal} | {strength:.2f} | {reason}")
            return signal, strength
        except:
            print(f"[{provider}] JSON не найден → fallback парсинг")

        # Fallback: парсим текст
        text = content.lower()
        if any(word in text for word in ["buy", "покупай", "long", "bullish"]):
            signal = "BUY"
            strength = 0.75
        elif any(word in text for word in ["sell", "продавай", "short", "bearish"]):
            signal = "SELL"
            strength = 0.75
        else:
            signal = "HOLD"
            strength = 0.5

        reason = content.split("\n")[0][:25]
        print(f"[{provider}] {signal} | {strength:.2f} | {reason}")
        return signal, strength
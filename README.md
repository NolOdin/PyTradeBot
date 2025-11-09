# **ETH/USDT Trading Bot MVP**  
**Полный, масштабируемый торговый бот на Bybit (спот) с AI, бэктестом, оптимизацией и Telegram-уведомлениями**

---

## Содержание
1. [Обзор проекта](#обзор-проекта)  
2. [Функциональность](#функциональность)  
3. [Структура проекта](#структура-проекта)  
4. [Требования](#требования)  
5. [Установка и настройка](#установка-и-настройка)  
6. [Запуск](#запуск)  
7. [Режимы работы](#режимы-работы)  
8. [Безопасность](#безопасность)  
9. [Масштабирование](#масштабирование)  
10. [FAQ](#faq)  

---

<a name="обзор-проекта"></a>
## Обзор проекта

**ETH/USDT Trading Bot MVP** — это **полностью рабочий, модульный и масштабируемый торговый бот**, который:

- Торгует **на споте ETH/USDT** через **Bybit API**
- Использует **AI (DeepSeek)** для генерации сигналов
- Сохраняет **историю сделок** в SQLite
- Обучается на истории с помощью **scikit-learn**
- Поддерживает **бэктест с графиками**
- **Оптимизирует параметры** (Grid Search + Walk-Forward)
- Отправляет **алерты в Telegram**
- Готов к **Docker, продакшн, масштабированию**

---

<a name="функциональность"></a>
## Функциональность

| Функция | Статус |
|--------|--------|
| Торговля на Bybit (спот) | Done |
| AI-сигналы (DeepSeek) | Done |
| Сохранение истории (SQLite) | Done |
| ML-обучение на сделках | Done |
| Бэктест с графиком | Done |
| Оптимизация параметров | Done |
| Telegram-алерты | Done |
| Авто-применение лучших параметров | Done |
| Логирование | Done |
| Тестнет / продакшн | Done |

---

<a name="структура-проекта"></a>
## Структура проекта

```bash
eth_bot_mvp/
├── main.py              # Точка входа
├── config.py            # Конфигурация (ключи, параметры)
├── trade_engine.py      # Логика торговли
├── ai_predictor.py      # DeepSeek AI
├── data_manager.py      # SQLite: история сделок
├── ml_learner.py        # ML-обучение
├── monitor.py           # Логирование
├── backtest.py          # Бэктест + график
├── optimizer.py         # Оптимизация (Grid Search)
├── best_params.json     # ← создаётся после --optimize
├── trades.db            # ← создаётся после первой сделки
├── bot.log              # Логи
└── README.md            # Этот файл
```

---

<a name="требования"></a>
## Требования

| Зависимость | Версия |
|-----------|--------|
| Python | `>=3.10` |
| ccxt | `>=4.0` |
| pandas | `>=1.5` |
| scikit-learn | `>=1.2` |
| requests | `>=2.28` |
| python-telegram-bot | `>=20.0` |
| matplotlib | `>=3.7` |

---

<a name="установка-и-настройка"></a>
## Установка и настройка

### 1. Клонируй репозиторий
```bash
git clone https://github.com/yourname/eth_bot_mvp.git
cd eth_bot_mvp
```

### 2. Установи зависимости
```bash
pip install ccxt pandas scikit-learn requests python-telegram-bot matplotlib
```

### 3. Настрой `.env` (рекомендуется)
Создай файл `.env`:
```env
BYBIT_API_KEY=your_bybit_api_key
BYBIT_SECRET=your_bybit_secret
DEEPSEEK_API_KEY=your_deepseek_key
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

> Или используй `export VAR=value` в терминале.

---

<a name="запуск"></a>
## Запуск

```bash
python main.py [режим]
```

| Режим | Команда |
|------|--------|
| **Живая торговля** | `python main.py` |
| **Бэктест** | `python main.py --backtest --days 90` |
| **Оптимизация** | `python main.py --optimize` |

---

<a name="режимы-работы"></a>
## Режимы работы

### 1. Оптимизация параметров
```bash
python main.py --optimize
```
- Перебирает `stop_loss`, `take_profit`, `ai_threshold`
- Сохраняет **лучшие** в `best_params.json`
- Отправляет отчёт в Telegram

### 2. Бэктест
```bash
python main.py --backtest --days 90
```
- Загружает OHLCV с Bybit
- Показывает **график с сделками**
- Выводит: доходность, Sharpe, Win Rate, Max Drawdown

### 3. Живая торговля
```bash
python main.py
```
- Работает в цикле (каждую минуту)
- Использует **лучшие параметры** из `best_params.json`
- Логирует в `bot.log`
- Отправляет алерты в Telegram

---

<a name="безопасность"></a>
## Безопасность

| Мера | Как включить |
|------|-------------|
| **Тестнет** | `sandbox: True` в `trade_engine.py` |
| **Малый размер** | `AMOUNT_ETH = 0.001` |
| **Стоп-лосс** | 2% по умолчанию |
| **IP-whitelist** | В настройках Bybit API |
| **.env** | Не коммить ключи |

> **Никогда не запускай в продакшене без тестов!**

---

<a name="масштабирование"></a>
## Масштабирование

| Направление | Как реализовать |
|------------|------------------|
| **Другие пары** | `config.py → SYMBOL = 'BTC/USDT'` |
| **Фьючерсы** | `defaultType: 'future'` в ccxt |
| **Docker** | `docker-compose up -d` |
| **Веб-дашборд** | Flask + Plotly |
| **Авто-оптимизация** | `cron` + `--optimize` |

---

<a name="faq"></a>
## FAQ

### Где ключи от Bybit?
→ [Bybit API Management](https://www.bybit.com/app/user/api-management)

### Где тестнет?
→ [Bybit Testnet](https://testnet.bybit.com)

### Как включить реальную торговлю?
```python
# trade_engine.py
self.exchange = ccxt.bybit({
    'apiKey': BYBIT_API_KEY,
    'secret': BYBIT_SECRET,
    'enableRateLimit': True,
    'sandbox': False  # ← ИЗМЕНИТЬ
})
```

### Где логи?
→ `bot.log` и `trades.db` (открыть в DB Browser for SQLite)

### Как посмотреть историю сделок?
```sql
SELECT * FROM trades ORDER BY timestamp DESC LIMIT 10;
```

---

## Лицензия

**MIT** — используй, модифицируй, продавай.  
*Торговля — рискованно. Используй на свой страх и риск.*

---

## Готов к запуску!

```bash
python main.py --optimize
python main.py --backtest
python main.py
```

---

**Разработано с помощью Grok (xAI)**  
**Удачи в трейдинге!**

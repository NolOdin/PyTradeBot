# Инструкция по развертыванию ETH/USDT Trading Bot

## 🚀 Быстрый старт

### 1. Требования
- Python 3.10 или выше
- Доступ к Bybit API (не заблокирован в вашей локации)
- API ключи от Bybit и DeepSeek (или OpenRouter)

### 2. Установка на локальной машине

```bash
# Клонируйте проект или скачайте архив
git clone <your-repo-url>
cd eth_bot_mvp

# Создайте виртуальное окружение (рекомендуется)
python -m venv venv

# Активируйте виртуальное окружение
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Установите зависимости
pip install -r reqs.txt
```

### 3. Настройка переменных окружения

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Откройте `.env` и заполните ваши API ключи:

```env
BYBIT_API_KEY=ваш_ключ_bybit
BYBIT_SECRET=ваш_секрет_bybit
DEEPSEEK_API_KEY=ваш_ключ_deepseek
```

**Получение API ключей:**
- **Bybit**: https://www.bybit.com/app/user/api-management
- **Bybit Testnet**: https://testnet.bybit.com
- **DeepSeek**: https://platform.deepseek.com
- **OpenRouter** (альтернатива): https://openrouter.ai

### 4. Запуск бота

#### Режим 1: Оптимизация параметров (рекомендуется начать с этого)
```bash
python main.py --optimize
```
Найдет оптимальные параметры и сохранит в `best_params.json`

#### Режим 2: Бэктест на исторических данных
```bash
python main.py --backtest --days 90
```
Протестирует стратегию на данных за последние 90 дней

#### Режим 3: Живая торговля
```bash
python main.py
```
Запустит бота в режиме реальной торговли (по умолчанию на тестнете)

## 🔧 Переход на реальную торговлю

1. Откройте `trade_engine.py`
2. Найдите строку: `'sandbox': True`
3. Измените на: `'sandbox': False`

⚠️ **ВНИМАНИЕ**: Начинайте с малых сумм! По умолчанию - 0.01 ETH

## 📊 Развертывание на VPS

### Ubuntu/Debian VPS

```bash
# Обновите систему
sudo apt update && sudo apt upgrade -y

# Установите Python и pip
sudo apt install python3 python3-pip python3-venv -y

# Загрузите проект
git clone <your-repo-url>
cd eth_bot_mvp

# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установите зависимости
pip install -r reqs.txt

# Настройте .env файл
nano .env
# (вставьте ваши ключи и сохраните)

# Запустите в фоновом режиме
nohup python main.py > bot.log 2>&1 &

# Проверьте логи
tail -f bot.log
```

### Автозапуск через systemd (Linux)

Создайте файл `/etc/systemd/system/trading-bot.service`:

```ini
[Unit]
Description=ETH/USDT Trading Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/eth_bot_mvp
Environment="PATH=/path/to/eth_bot_mvp/venv/bin"
ExecStart=/path/to/eth_bot_mvp/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Активируйте сервис:
```bash
sudo systemctl daemon-reload
sudo systemctl enable trading-bot
sudo systemctl start trading-bot
sudo systemctl status trading-bot
```

## 🐳 Развертывание через Docker

Создайте `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY reqs.txt .
RUN pip install --no-cache-dir -r reqs.txt

COPY . .

CMD ["python", "main.py"]
```

Создайте `docker-compose.yml`:

```yaml
version: '3.8'

services:
  trading-bot:
    build: .
    env_file:
      - .env
    restart: unless-stopped
    volumes:
      - ./trades.db:/app/trades.db
      - ./bot.log:/app/bot.log
      - ./best_params.json:/app/best_params.json
```

Запустите:
```bash
docker-compose up -d
docker-compose logs -f
```

## 📱 Настройка Telegram уведомлений (опционально)

1. Создайте бота через [@BotFather](https://t.me/BotFather)
2. Скопируйте токен бота
3. Получите ваш Chat ID через [@userinfobot](https://t.me/userinfobot)
4. Добавьте в `.env`:
   ```env
   TELEGRAM_TOKEN=ваш_токен_бота
   TELEGRAM_CHAT_ID=ваш_chat_id
   ```

## 🔍 Мониторинг и логи

- **Логи бота**: `bot.log`
- **База данных сделок**: `trades.db`
- **Лучшие параметры**: `best_params.json`

Просмотр сделок:
```bash
sqlite3 trades.db "SELECT * FROM trades ORDER BY timestamp DESC LIMIT 10;"
```

## ⚙️ Настройка параметров

Отредактируйте `config.py`:

```python
SYMBOL = 'ETH/USDT'        # Торговая пара
AMOUNT_ETH = 0.01          # Размер позиции
STOP_LOSS_PCT = 0.02       # Стоп-лосс 2%
TAKE_PROFIT_PCT = 0.05     # Тейк-профит 5%
```

## 🛡️ Безопасность

- ✅ Всегда начинайте с тестнета (`sandbox: True`)
- ✅ Используйте малые суммы для начала
- ✅ Настройте IP whitelist в Bybit API
- ✅ Никогда не коммитьте `.env` в git
- ✅ Регулярно проверяйте логи
- ✅ Включите стоп-лосс

## 📈 Масштабирование

- **Другие пары**: измените `SYMBOL` в `config.py`
- **Фьючерсы**: добавьте `'defaultType': 'future'` в ccxt
- **Множественные пары**: запустите несколько экземпляров бота
- **Web-интерфейс**: добавьте Flask/Streamlit dashboard

## 🆘 Решение проблем

### Ошибка 403 Forbidden
- Проверьте, не заблокирован ли Bybit API в вашей локации
- Используйте VPN или прокси
- Убедитесь, что API ключи правильные

### Бот не торгует
- Проверьте настройки `ai_threshold` в `best_params.json`
- Убедитесь, что DeepSeek API ключ активен
- Проверьте логи на наличие ошибок

### Недостаточно средств
- Пополните баланс на Bybit
- Уменьшите `AMOUNT_ETH` в config.py

## 📞 Поддержка

- Проверьте логи: `tail -f bot.log`
- Проверьте историю сделок: `sqlite3 trades.db`
- Запустите бэктест для проверки стратегии

---

## ✅ Чеклист перед запуском

- [ ] Python 3.10+ установлен
- [ ] Зависимости установлены (`pip install -r reqs.txt`)
- [ ] Файл `.env` создан и заполнен
- [ ] API ключи Bybit созданы
- [ ] API ключ DeepSeek получен
- [ ] Запущена оптимизация (`--optimize`)
- [ ] Проведен бэктест (`--backtest`)
- [ ] Режим sandbox для начала (`sandbox: True`)
- [ ] Малый размер позиции для начала
- [ ] Настроен мониторинг логов

**Удачи в трейдинге! 🚀📈**

ollama pull llama3.2
ollama serve 


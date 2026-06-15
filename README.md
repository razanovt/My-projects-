# My-projects-
# 🚀 CryptoDropHunter Telegram Bot

A Telegram bot that automatically discovers and tracks new cryptocurrency airdrops from popular sources.

The bot periodically scans trusted airdrop websites, stores new opportunities in a SQLite database, and instantly notifies subscribed users when new airdrops become available.

---

# ✨ Features

* 📡 Automatic airdrop monitoring
* 🔍 Data collection from:

  * Airdrops.io
  * CoinMarketCap Airdrops
* 💾 SQLite database storage
* 📨 Instant notifications for new airdrops
* ✅ Mark completed airdrops
* 👤 User registration via `/start`
* ⭐ Premium user support (prepared for future features)
* 📝 Detailed logging system

---

# 🛠 Tech Stack

* Python 3.10+
* python-telegram-bot 20+
* SQLite3
* HTTPX
* BeautifulSoup4
* python-dotenv

---

# 📂 Project Structure

```text
project/
│
├── bot.py
├── .env
├── airdrops.db
├── logs/
│   └── bot.log
│
└── README.md
```

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/yourusername/cryptodrophunter.git

cd cryptodrophunter
```

## 2. Create a Virtual Environment

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install python-telegram-bot httpx beautifulsoup4 python-dotenv
```

---

# 🔑 Configuration

Create a `.env` file in the project root directory:

```env
BOT_TOKEN=your_telegram_bot_token
```

You can obtain a Telegram Bot Token from BotFather.

---

# ▶️ Running the Bot

```bash
python bot.py
```

After startup, you should see:

```text
🚀 Bot started successfully and is ready to work.
```

---

# 🤖 Bot Commands

## `/start`

Registers the user and displays a welcome message.

## `/airdrops`

Shows the latest 5 discovered airdrops.

---

# 💾 Database Schema

The bot automatically creates the following tables:

## users

```sql
id INTEGER PRIMARY KEY
premium INTEGER DEFAULT 0
```

## airdrops

```sql
name TEXT PRIMARY KEY
link TEXT
reward TEXT
difficulty TEXT
deadline TEXT
```

## completed

```sql
user_id INTEGER
airdrop TEXT
```

---

# 🔄 Automatic Updates

The bot checks for new airdrops every hour:

```python
app.job_queue.run_repeating(
    check_airdrops,
    interval=3600,
    first=10
)
```

You can modify the interval according to your needs.

---

# 📢 Notifications

When a new airdrop is found, all registered users receive a notification:

```text
🚨 New Airdrop!

💎 Project Name
🏆 Reward
⚙️ Difficulty
⏰ Deadline

🔗 Link
```

---

# 📝 Logging

All events are stored in:

```text
logs/bot.log
```

The bot logs:

* Startup events
* Parsing errors
* Message delivery errors
* Newly discovered airdrops
* System exceptions

---

# ⭐ Premium Features (Planned)

The codebase already includes support for premium users.

Future premium features may include:

* Blockchain network filtering (Ethereum, Solana, Base, etc.)
* Difficulty-based filtering
* High-value airdrop alerts
* Personalized recommendations
* Advanced statistics

---

# 🔒 Security

Never store your Telegram token directly in the source code.

Use environment variables instead:

```env
BOT_TOKEN=xxxxxxxxxxxxxxxx
```

It is strongly recommended to add `.env` to your `.gitignore` file.

---

# 📄 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

CryptoDropHunter

A Telegram bot designed to automate the discovery and tracking of promising cryptocurrency airdrops.

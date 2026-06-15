# 🎙️ Discord Voice Anti-Spam Bot

A Discord moderation bot designed to monitor voice channel activity, log user movements, detect voice channel spam, and automatically mute offenders.

The bot helps server administrators prevent users from repeatedly joining, leaving, or switching voice channels to disrupt the community.

---

# ✨ Features

### 📊 Voice Activity Logging

Logs all voice channel events:

* User joins a voice channel
* User leaves a voice channel
* User switches between voice channels

Example:

```text
📥 User joined General
📤 User left General
🔄 User moved from General to Music
```

---

### 🚨 Voice Spam Detection

The bot tracks how often users join or switch voice channels.

If a user exceeds the configured limit:

* Receives a mute role
* Gets server-muted
* Is disconnected from the voice channel
* Action is logged automatically

---

### 🔊 Automatic Unmute

Muted users are automatically unmuted after the configured timeout.

---

### 🛡️ Immunity Roles

Staff members or trusted users can be excluded from anti-spam checks.

Examples:

* Administrators
* Moderators
* VIP Members

---

### 🎧 Persistent Voice Connection

The bot automatically joins a specified voice channel on startup and remains connected.

---

# 🛠 Technologies

* Python 3.10+
* discord.py 2.x
* asyncio

---

# 📦 Installation

## Clone the Repository

```bash
git clone https://github.com/yourusername/discord-voice-antispam-bot.git

cd discord-voice-antispam-bot
```

## Create Virtual Environment

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

## Install Dependencies

```bash
pip install -U discord.py
```

---

# ⚙️ Configuration

Open the source file and configure the following values:

```python
LOG_CHANNEL_ID = 1234567890123456789
MUTE_ROLE_ID = 1234567890123456789

VOICE_CHANNEL_ID = 1234567890123456789

ALLOWED_VOICE_CHANNELS = [
    1234567890123456789
]

IMMUNE_ROLES = [
    1234567890123456789
]
```

---

## Anti-Spam Settings

```python
MUTE_TIME = 600
SPAM_LIMIT = 5
SPAM_WINDOW = 30
```

### Parameters

| Parameter   | Description                    |
| ----------- | ------------------------------ |
| MUTE_TIME   | Mute duration in seconds       |
| SPAM_LIMIT  | Maximum allowed voice actions  |
| SPAM_WINDOW | Time window for spam detection |

Default behavior:

```text
5 joins/moves within 30 seconds
→ User receives a 10-minute mute
```

---

# 🔑 Bot Token

Replace:

```python
bot.run("Your Token")
```

with:

```python
bot.run("YOUR_DISCORD_BOT_TOKEN")
```

For better security, use environment variables:

```python
import os

bot.run(os.getenv("DISCORD_TOKEN"))
```

---

# ▶️ Running the Bot

```bash
python bot.py
```

Expected output:

```text
Bot started as MyBot#1234
Connected to voice channel: General
```

---

# 📋 Permissions Required

The bot should have the following permissions:

* View Channels
* Connect
* Speak
* Move Members
* Mute Members
* Manage Roles
* Send Messages
* Read Message History

---

# 🚨 Anti-Spam Workflow

1. User joins or switches voice channels.
2. Activity is recorded.
3. If the user exceeds the configured threshold:

   * Mute role is assigned.
   * User is server-muted.
   * User is disconnected.
   * Moderation log is created.
4. After the mute duration:

   * Mute role is removed automatically.

---

# 📝 Logging

The bot sends moderation logs to the configured log channel.

Examples:

```text
📥 User joined General

🔄 User moved from General to Music

🚨 User muted for 10 minutes due to voice spam

🔊 User automatically unmuted
```

---

# 🛡️ Security Recommendations

Do not hardcode your bot token.

Create a `.env` file:

```env
DISCORD_TOKEN=your_token_here
```

Then load it using:

```python
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
```

---

# 📄 License

MIT License

---

# 👨‍💻 Author

Discord Voice Anti-Spam Bot

A lightweight moderation bot for preventing voice channel flooding and abuse.

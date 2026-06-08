import asyncio
import httpx
import logging
import os
from dotenv import load_dotenv
import sqlite3
import sys
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, Defaults
)

# --- Загрузка переменных окружения ---
load_dotenv()  # обязательно вызвать ДО получения переменных

BOT_TOKEN = os.getenv("BOT_TOKEN") # получаем токен из переменной окружения

if not BOT_TOKEN:
    raise ValueError("Не найден токен Telegram. Проверьте переменную окружения BOT_TOKEN")

LOG_DIR = "logs"
DB_PATH = "airdrops.db"

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler(f"{LOG_DIR}/bot.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ],
)
logger = logging.getLogger(__name__)

# --- База данных ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, premium INTEGER DEFAULT 0)")
    c.execute("CREATE TABLE IF NOT EXISTS airdrops (name TEXT PRIMARY KEY, link TEXT, reward TEXT, difficulty TEXT, deadline TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS completed (user_id INTEGER, airdrop TEXT)")
    conn.commit()
    conn.close()

def is_premium(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT premium FROM users WHERE id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result and result[0] == 1

def add_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def save_airdrop(airdrop):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO airdrops VALUES (?, ?, ?, ?, ?)", (
            airdrop['name'], airdrop['link'], airdrop['reward'],
            airdrop['difficulty'], airdrop['deadline']
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def mark_completed(user_id, airdrop_name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO completed (user_id, airdrop) VALUES (?, ?)", (user_id, airdrop_name))
    conn.commit()
    conn.close()

# --- Команды ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id)
    await update.message.reply_text(
        "👋 Добро пожаловать в CryptoDropHunter!\n"
        "🪂 Я отслеживаю новые airdrops и отправляю только реальные и ценные.\n"
        "📌 Используй /airdrops для просмотра.\n"
        "✨ Premium пользователи получают фильтрацию по сложности и сети."
    )

async def show_airdrops(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM airdrops ORDER BY rowid DESC LIMIT 5")
    drops = c.fetchall()
    conn.close()

    if not drops:
        await update.message.reply_text("❌ Пока нет новых airdrop'ов.")
        return

    for drop in drops:
        name, link, reward, diff, deadline = drop
        buttons = [
            [
                InlineKeyboardButton("✅ Выполнено", callback_data=f"done:{name}"),
                InlineKeyboardButton("📋 Инструкция", url=link)
            ]
        ]
        await update.message.reply_text(
            f"*💎 Airdrop: {name}*\n"
            f"🏆 Награда: {reward}\n"
            f"⚙️ Сложность: {diff}\n"
            f"⏰ Срок: {deadline}",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )

# --- Callback ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data.startswith("done:"):
        name = query.data.split("done:")[1]
        mark_completed(user_id, name)
        await query.edit_message_text(f"✅ Airdrop «{name}» отмечен как выполненный!")

# --- Парсеры ---
async def fetch_airdrops_io():
    url = "https://airdrops.io/"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    cards = soup.find_all("div", class_="card")
    results = []
    for card in cards:
        try:
            name = card.find("h2").text.strip()
            link = card.find("a", href=True)["href"]
            reward = "—"
            diff = "—"
            deadline = "—"
            results.append({
                "name": name, "link": link,
                "reward": reward, "difficulty": diff, "deadline": deadline
            })
        except Exception as e:
            logger.debug(f"Error parsing airdrops.io card: {e}")
            continue
    return results

async def fetch_coinmarketcap():
    url = "https://coinmarketcap.com/airdrop/"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    blocks = soup.select("div[data-testid='airdrop-card']")
    results = []
    for block in blocks:
        try:
            name = block.select_one("h4").text.strip()
            link = "https://coinmarketcap.com" + block.find("a")["href"]
            reward = block.find(text=lambda t: "$" in t or "token" in t.lower()).strip()
            results.append({
                "name": name, "link": link,
                "reward": reward, "difficulty": "—", "deadline": "—"
            })
        except Exception as e:
            logger.debug(f"Error parsing coinmarketcap card: {e}")
            continue
    return results

# --- Обновление ---
async def check_airdrops(context: ContextTypes.DEFAULT_TYPE):
    app = context.application
    sources = [fetch_airdrops_io(), fetch_coinmarketcap()]
    all_new = []

    for task in await asyncio.gather(*sources):
        for drop in task:
            if save_airdrop(drop):
                all_new.append(drop)

    if all_new:
        logger.info(f"🆕 Найдено {len(all_new)} новых airdrop'ов.")
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id FROM users")
        users = [row[0] for row in c.fetchall()]
        conn.close()

        for drop in all_new:
            text = (
                f"🚨 *Новый Airdrop!*\n"
                f"💎 *{drop['name']}*\n"
                f"🏆 Награда: {drop['reward']}\n"
                f"⚙️ Сложность: {drop['difficulty']}\n"
                f"⏰ Срок: {drop['deadline']}\n"
                f"[🔗 Перейти]({drop['link']})"
            )
            for user_id in users:
                try:
                    await app.bot.send_message(user_id, text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
                except Exception as e:
                    logger.error(f"❌ Ошибка при отправке пользователю {user_id}: {e}")
    else:
        logger.info("🤖 Новых airdrop'ов не найдено")

# --- Запуск ---
def main():
    init_db()
    defaults = Defaults(parse_mode=ParseMode.MARKDOWN)
    app = Application.builder().token(BOT_TOKEN).defaults(defaults).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("airdrops", show_airdrops))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.job_queue.run_repeating(check_airdrops, interval=3600, first=10)

    logger.info("🚀 Бот запущен и готов к работе.")
    app.run_polling()

if __name__ == "__main__":
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        main()
    except Exception:
        logger.exception("Fatal error on startup:")
        raise

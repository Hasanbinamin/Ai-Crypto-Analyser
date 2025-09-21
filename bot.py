# bot.py (with JSON persistence for user signals)
import os
import re
import json
import httpx
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes
)
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = "http://127.0.0.1:8000/analyze"

DATA_FILE = "data/user_data.json"

# Runtime data
user_signals = {}   # persists in JSON
user_jobs = {}      # runtime only
user_loop_info = {} # runtime only

# -------- JSON PERSISTENCE -------- #
def load_user_data():
    global user_signals
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                user_signals = json.load(f)
        except Exception:
            user_signals = {}
    else:
        user_signals = {}

def save_user_data():
    with open(DATA_FILE, "w") as f:
        json.dump(user_signals, f, indent=4)

# -------- UI HELPERS -------- #
def main_menu():
    keyboard = [
        [InlineKeyboardButton("📈 Set Symbol", callback_data="set_symbol")],
        [InlineKeyboardButton("⏳ Set Timeframe", callback_data="set_timeframe")],
        [InlineKeyboardButton("💾 Save Signal", callback_data="save_signal")],
        [InlineKeyboardButton("🔁 Resend Signal", callback_data="resend_signal")],
        [InlineKeyboardButton("⏲ Enable Loop", callback_data="enable_loop")],
        [InlineKeyboardButton("🛑 Stop Loop", callback_data="stop_loop")]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_button():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back")]])

# -------- START -------- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚡ Choose an option:", reply_markup=main_menu())

# -------- BUTTON HANDLER -------- #
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)  # string for JSON keys

    if query.data == "set_symbol":
        await query.edit_message_text("Send me the trading symbol (e.g., BTCUSDT).", reply_markup=back_button())
        context.user_data["awaiting"] = "symbol"

    elif query.data == "set_timeframe":
        await query.edit_message_text("Send me the timeframe (e.g., 1h, 4h, 1d).", reply_markup=back_button())
        context.user_data["awaiting"] = "timeframe"

    elif query.data == "save_signal":
        if "symbol" in context.user_data and "timeframe" in context.user_data:
            user_signals[user_id] = {
                "symbol": context.user_data["symbol"],
                "timeframe": context.user_data["timeframe"],
            }
            save_user_data()  # persist to JSON
            await query.edit_message_text(f"✅ Saved signal: {user_signals[user_id]}", reply_markup=main_menu())
        else:
            await query.edit_message_text("⚠️ Please set symbol & timeframe first.", reply_markup=main_menu())

    elif query.data == "resend_signal":
        signal = user_signals.get(user_id)
        if signal:
            query_str = f"{signal['symbol']} {signal['timeframe']}"
            await send_analysis(user_id, context, query_str)
        else:
            await query.edit_message_text("⚠️ No saved signal found.", reply_markup=main_menu())

    elif query.data == "enable_loop":
        signal = user_signals.get(user_id)
        if signal:
            query_str = f"{signal['symbol']} {signal['timeframe']}"
            interval = timeframe_to_seconds(signal["timeframe"])
            if interval:
                if user_id in user_jobs:
                    user_jobs[user_id].schedule_removal()

                job = context.job_queue.run_repeating(
                    loop_task, interval=interval, first=0,
                    chat_id=int(user_id), data=query_str
                )
                user_jobs[user_id] = job
                next_run = datetime.now() + timedelta(seconds=interval)
                user_loop_info[user_id] = {"interval": interval, "next_run": next_run}

                await query.edit_message_text(
                    f"🔁 Loop enabled for {signal['symbol']} every {signal['timeframe']}.\n"
                    f"➡️ Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}",
                    reply_markup=main_menu()
                )
            else:
                await query.edit_message_text("⚠️ Unsupported timeframe.", reply_markup=main_menu())
        else:
            await query.edit_message_text("⚠️ Save a signal first.", reply_markup=main_menu())

    elif query.data == "stop_loop":
        if user_id in user_jobs:
            user_jobs[user_id].schedule_removal()
            del user_jobs[user_id]
            user_loop_info.pop(user_id, None)
            await query.edit_message_text("🛑 Loop stopped.", reply_markup=main_menu())
        else:
            await query.edit_message_text("⚠️ No loop is running.", reply_markup=main_menu())

    elif query.data == "back":
        await query.edit_message_text("⚡ Back to main menu:", reply_markup=main_menu())

# -------- TEXT HANDLER -------- #
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    awaiting = context.user_data.get("awaiting")

    if awaiting == "symbol":
        context.user_data["symbol"] = update.message.text.upper()
        await update.message.reply_text(f"✅ Symbol set: {context.user_data['symbol']}", reply_markup=main_menu())
        context.user_data["awaiting"] = None

    elif awaiting == "timeframe":
        context.user_data["timeframe"] = update.message.text
        await update.message.reply_text(f"✅ Timeframe set: {context.user_data['timeframe']}", reply_markup=main_menu())
        context.user_data["awaiting"] = None

    else:
        await update.message.reply_text("Use /start to configure signals.")

# -------- ANALYSIS -------- #
async def send_analysis(chat_id, context, query_str):
    try:
        async with httpx.AsyncClient(timeout=1000.0) as client:
            response = await client.post(API_URL, json={"query": query_str})
            data = response.json()
            result = data.get("result", "⚠️ No response from AI agent.")
    except Exception as e:
        result = f"❌ Error: {e}"
    await context.bot.send_message(chat_id=chat_id, text=result)

async def loop_task(context: ContextTypes.DEFAULT_TYPE):
    query_str = context.job.data
    await send_analysis(context.job.chat_id, context, query_str)
    user_loop_info[str(context.job.chat_id)]["next_run"] = datetime.now() + timedelta(
        seconds=user_loop_info[str(context.job.chat_id)]["interval"]
    )

# -------- UTILS -------- #
def timeframe_to_seconds(tf: str):
    tf = tf.strip().lower()
    match = re.match(r"(\d+)(m|h|d|w|mo|y)$", tf)
    if not match:
        return None
    value, unit = int(match.group(1)), match.group(2)
    multipliers = {
        "m": 60, "h": 3600, "d": 86400, "w": 604800,
        "mo": 2592000, "y": 31536000,
    }
    return value * multipliers.get(unit, 0)

# -------- MAIN -------- #
def main():
    load_user_data()  # load from JSON at startup

    app = Application.builder() \
        .token(BOT_TOKEN) \
        .connect_timeout(15) \
        .read_timeout(15) \
        .build()

    app.job_queue  # ensure job queue

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()

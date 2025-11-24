import telebot
import requests
import json
import re
from flask import Flask #𓍯𝙎𝙪𝙟𝙖𝙡⚝
from telebot.apihelper import ApiTelegramException #𓍯𝙎𝙪𝙟𝙖𝙡⚝

# ----------------------- CONFIG -----------------------
TOKEN = "8266651898:AAFTdgzKg9Cse8Wzw8aoH6XuDJ7TZ2-RefU"  # Replace with your bot token
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

app = Flask("render_web") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
def safe_send(send_func, *args, **kwargs): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    try: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        return send_func(*args, **kwargs) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    except Exception as e: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        print(f"[safe_send error] {e}") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        return None #𓍯𝙎𝙪𝙟𝙖𝙡⚝

@app.route("/") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
def home(): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    return "✅ Bot is running on Render!" #𓍯𝙎𝙪𝙟𝙖𝙡⚝

BASE_API = "https://api.b77bf911.workers.dev"
ENDPOINTS = {
    'mobile': f'{BASE_API}/mobile?number=',
    'aadhaar': f'{BASE_API}/aadhaar?id=',
    'gst': f'{BASE_API}/gst?number=',
    'telegram': f'{BASE_API}/telegram?user=',
    'ifsc': f'{BASE_API}/ifsc?code=',
    'rashan': f'{BASE_API}/rashan?aadhaar=',
    'vehicle': f'{BASE_API}/vehicle?registration='
}

user_state = {}

# ----------------------- CLEAN & PRETTY FORMATTER -----------------------
def clean_text(text):
    if text is None:
        return ""
    text = str(text)
    text = text.replace("!", ", ")
    text = re.sub(r"\s*,\s*", ", ", text)
    text = re.sub(r",\s*(,|\s)+", ", ", text)
    text = text.strip(" ,\n\t")
    text = text.replace("*", "").replace("_", "").replace("`", "")
    return text

def pretty_address(raw):
    if not raw:
        return ""
    parts = re.split(r"[!|;\/\\\n]+", str(raw))
    parts = [clean_text(p) for p in parts if p.strip()]
    seen = set()
    out = []
    for p in parts:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return ", ".join(out)

def pretty_format(data, indent=2):
    """Recursive pretty format for any JSON structure."""
    if isinstance(data, dict):
        text = ""
        for k, v in data.items():
            if v in [None, "", "N/A"]:
                continue
            key = str(k).replace("_", " ").title()
            text += f"🔹 **{key}:** {pretty_format(v)}\n"
        return text
    elif isinstance(data, list):
        text = ""
        for i, item in enumerate(data, 1):
            text += f"\n------ 🌸 Record 🌸{i} ------\n"
            text += pretty_format(item)
        return text
    else:
        return str(data)

# ----------------------- START COMMAND -----------------------
@bot.message_handler(commands=['start', 'help'])
def start(msg):
    text = "**🔍 OSINT Lookup Bot**\nChoose the service:"
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(
        telebot.types.InlineKeyboardButton("📱 Mobile", callback_data="mobile"),
        telebot.types.InlineKeyboardButton("🆔 Aadhaar", callback_data="aadhaar")
    )
    kb.add(
        telebot.types.InlineKeyboardButton("🧾 GST", callback_data="gst"),
        telebot.types.InlineKeyboardButton("💬 Telegram", callback_data="telegram")
    )
    kb.add(
        telebot.types.InlineKeyboardButton("🏦 IFSC", callback_data="ifsc"),
        telebot.types.InlineKeyboardButton("🍚 Ration", callback_data="rashan")
    )
    kb.add(
        telebot.types.InlineKeyboardButton("🚗 Vehicle", callback_data="vehicle")
    )
    bot.send_message(msg.chat.id, text, reply_markup=kb)

# ----------------------- CALLBACK -----------------------
@bot.callback_query_handler(func=lambda c: True)
def callback(call):
    user_state[call.from_user.id] = call.data
    prompts = {
        "mobile": "📱 Send Mobile Number:",
        "aadhaar": "🆔 Send Aadhaar ID:",
        "gst": "🧾 Send GST Number:",
        "telegram": "💬 Send Telegram Username:",
        "ifsc": "🏦 Send IFSC Code:",
        "rashan": "🍚 Send Aadhaar Number for Ration Info:",
        "vehicle": "🚗 Send Vehicle Number:"
    }
    bot.send_message(call.message.chat.id, prompts.get(call.data, "Send Input"))

# ----------------------- USER INPUT -----------------------
@bot.message_handler(func=lambda m: m.from_user.id in user_state)
def handle_input(msg):
    user_id = msg.from_user.id
    service = user_state[user_id]
    value = msg.text.strip()

    url = ENDPOINTS[service] + requests.utils.quote(value)

    try:
        response = requests.get(url, timeout=10).json()
    except Exception as e:
        bot.send_message(msg.chat.id, f"❌ API Error: {e}")
        return

    data = response.get("data") or response.get("result") or response.get("info") or response

    formatted = pretty_format(data)
    final_msg = f"### 🔍 **{service.upper()} Result**\n\n{formatted}"

    bot.send_message(msg.chat.id, final_msg, parse_mode="Markdown")
    user_state.pop(user_id)

# ----------------------- RUN -----------------------
if __name__ == "__main__": #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    logging.info("Bot starting...") #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    # Flask को separate thread में चलाओ ताकि Render port detect कर सके #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    def run_flask(): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        port = int(os.environ.get("PORT", 10000)) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        app.run(host="0.0.0.0", port=port) #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    Thread(target=run_flask, daemon=True).start() #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    # Bot start #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    try: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        bot.infinity_polling(timeout=60, long_polling_timeout=60) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    except KeyboardInterrupt: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        logging.info("Bot stopped by user.") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    except Exception: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        logging.exception("Bot crashed") #𓍯𝙎𝙪𝙟𝙖𝙡⚝

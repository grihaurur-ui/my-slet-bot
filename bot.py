import json
import logging
import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ========== НАСТРОЙКИ ==========
TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = int(os.environ.get("CHAT_ID", "0"))
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
DATA_FILE = "data.json"

# ========== СПИСОК СЕРВЕРОВ ==========
SERVERS = [
    "🎉 NORILSK",
    "🦈 CHEREPOVETS",
    "💨 MAGADAN",
    "🏰 PODOLSK",
    "🏙 SURGUT",
    "🏍 IZHEVSK",
    "🎄 TOMSK",
    "🐿 TVER",
    "🐦‍🔥 VOLOGDA",
    "🦁 TAGANROG",
    "🌼 NOVGOROD",
    "🫐 KALUGA",
    "😹 VLADIMIR",
    "🐲 KOSTROMA",
    "🦎 CHITA",
    "🧣 ASTRAKHAN",
    "👜 BRATSK",
    "🥐 TAMBOV",
    "🥽 YAKUTSK",
    "🍭 ULYANOVSK",
    "🎈 LIPETSK",
    "💦 BARNAUL",
    "🏛 YAROSLAVL",
    "🦅 OREL",
    "🧸 BRYANSK",
    "🪭 PSKOV",
    "🫚 SMOLENSK",
    "🪼 STAVROPOL",
    "🪅 IVANOVO",
    "🪸 TOLYATTI",
    "🐋 TYUMEN",
    "🌺 KEMEROVO",
    "🔫 KIROV",
    "🍖 ORENBURG",
    "🥋 ARKHANGELSK",
    "🃏 KURSK",
    "🎳 MURMANSK",
    "🎷 PENZA",
    "🎭 RYAZAN",
    "⛳ TULA",
    "🏟 PERM",
    "🐨 KHABAROVSK",
    "🪄 CHEBOKSARY",
    "🖇 KRASNOYARSK",
    "🕊 CHELYABINSK",
    "👒 KALININGRAD",
    "🧶 VLADIVOSTOK",
    "🌂 VLADIKAVKAZ",
    "⛑️ MAKHACHKALA",
    "🎓 BELGOROD",
    "👑 VORONEZH",
    "🎒 VOLGOGRAD",
    "🌪 IRKUTSK",
    "🪙 OMSK",
    "🐉 SARATOV",
    "🍙 GROZNY",
    "🍃 NOVOSIB",
    "🪿 ARZAMAS",
    "🪻 KRASNODAR",
    "📗 EKB",
    "🪺 ANAPA",
    "🍺 ROSTOV",
    "🎧 SAMARA",
    "🏛 KAZAN",
    "🌊 SOCHI",
    "🌪 UFA",
    "🌉 SPB",
    "🌇 MOSCOW",
    "🤎 COCO",
    "📕 CHILLI",
    "❄ LCE",
    "📓 GRAY",
    "📘 AQUA",
    "🩶 PLATINUM",
    "💙 AQURE",
    "💛 GOLD",
    "❤‍🔥 CRIMSON",
    "🩷 MAGENTA",
    "🤍 WHITE",
    "💜 INDIGO",
    "🖤 BLACK",
    "🍒 CHERRY",
    "💕 PINK",
    "🍋 LIME",
    "💜 PURPLE",
    "🧡 ORANGE",
    "💛 YELLOW",
    "💙 BLUE",
    "💚 GREEN",
    "❤ RED"
]

# ========== СИНОНИМЫ ==========
SYNONYMS = {
    # Цвета
    "ВАЙТ": "WHITE", "БЕЛЫЙ": "WHITE",
    "БЛУ": "BLUE", "СИНИЙ": "BLUE",
    "ГРИН": "GREEN", "ЗЕЛЕНЫЙ": "GREEN",
    "ГОЛД": "GOLD", "ЗОЛОТО": "GOLD",
    "ПИНК": "PINK", "РОЗОВЫЙ": "PINK",
    "БЛЭК": "BLACK", "ЧЕРНЫЙ": "BLACK",
    "РЭД": "RED", "РЕД": "RED", "КРАСНЫЙ": "RED",
    "ОРАНЖ": "ORANGE", "ОРАНЖЕВЫЙ": "ORANGE",
    "ПЁРПЛ": "PURPLE", "ПУРПЛ": "PURPLE", "ФИОЛЕТОВЫЙ": "PURPLE",
    "ЛАЙМ": "LIME",
    "ЧЕРРИ": "CHERRY", "ВИШНЯ": "CHERRY",
    "ИНДИГО": "INDIGO",
    "МАДЖЕНТА": "MAGENTA",
    "КРИМСОН": "CRIMSON",
    "АКВА": "AQUA",
    "ГРЕЙ": "GRAY", "СЕРЫЙ": "GRAY",
    "ЛЦЕ": "LCE",
    "ЧИЛЛИ": "CHILLI",
    "КОКО": "COCO",
    "ПЛАТИНУМ": "PLATINUM",
    "АКУРЕ": "AQURE",

    # Города
    "МОСКВА": "MOSCOW",
    "ПИТЕР": "SPB", "СПБ": "SPB",
    "КАЗАНЬ": "KAZAN",
    "ЕКБ": "EKB", "ЕКАТЕРИНБУРГ": "EKB",
    "НОВОСИБ": "NOVOSIB", "НОВОСИБИРСК": "NOVOSIB",
    "КРАСНОДАР": "KRASNODAR",
    "СОЧИ": "SOCHI",
    "УФА": "UFA",
    "РОСТОВ": "ROSTOV",
    "САМАРА": "SAMARA",
    "НИЖНИЙ НОВГОРОД": "NOVGOROD", "НН": "NOVGOROD",
    "НОРИЛЬСК": "NORILSK",
    "ЧЕРЕПОВЕЦ": "CHEREPOVETS",
    "МАГАДАН": "MAGADAN",
    "ПОДОЛЬСК": "PODOLSK",
    "СУРГУТ": "SURGUT",
    "ИЖЕВСК": "IZHEVSK",
    "ТОМСК": "TOMSK",
    "ТВЕРЬ": "TVER",
    "ВОЛОГДА": "VOLOGDA",
    "ТАГАНРОГ": "TAGANROG",
    "КАЛУГА": "KALUGA",
    "ВЛАДИМИР": "VLADIMIR",
    "КОСТРОМА": "KOSTROMA",
    "ЧИТА": "CHITA",
    "АСТРАХАНЬ": "ASTRAKHAN",
    "БРАТСК": "BRATSK",
    "ТАМБОВ": "TAMBOV",
    "ЯКУТСК": "YAKUTSK",
    "УЛЬЯНОВСК": "ULYANOVSK",
    "ЛИПЕЦК": "LIPETSK",
    "БАРНАУЛ": "BARNAUL",
    "ЯРОСЛАВЛЬ": "YAROSLAVL",
    "ОРЕЛ": "OREL",
    "БРЯНСК": "BRYANSK",
    "ПСКОВ": "PSKOV",
    "СМОЛЕНСК": "SMOLENSK",
    "СТАВРОПОЛЬ": "STAVROPOL",
    "ИВАНОВО": "IVANOVO",
    "ТОЛЬЯТТИ": "TOLYATTI",
    "ТЮМЕНЬ": "TYUMEN",
    "КЕМЕРОВО": "KEMEROVO",
    "КИРОВ": "KIROV",
    "ОРЕНБУРГ": "ORENBURG",
    "АРХАНГЕЛЬСК": "ARKHANGELSK",
    "КУРСК": "KURSK",
    "МУРМАНСК": "MURMANSK",
    "ПЕНЗА": "PENZA",
    "РЯЗАНЬ": "RYAZAN",
    "ТУЛА": "TULA",
    "ПЕРМЬ": "PERM",
    "ХАБАРОВСК": "KHABAROVSK",
    "ЧЕБОКСАРЫ": "CHEBOKSARY",
    "КРАСНОЯРСК": "KRASNOYARSK",
    "ЧЕЛЯБИНСК": "CHELYABINSK",
    "КАЛИНИНГРАД": "KALININGRAD",
    "ВЛАДИВОСТОК": "VLADIVOSTOK",
    "ВЛАДИКАВКАЗ": "VLADIKAVKAZ",
    "МАХАЧКАЛА": "MAKHACHKALA",
    "БЕЛГОРОД": "BELGOROD",
    "ВОРОНЕЖ": "VORONEZH",
    "ВОЛГОГРАД": "VOLGOGRAD",
    "ИРКУТСК": "IRKUTSK",
    "ОМСК": "OMSK",
    "САРАТОВ": "SARATOV",
    "ГРОЗНЫЙ": "GROZNY",
    "АРЗАМАС": "ARZAMAS",
}

# ========== ЗАГРУЗКА ДАННЫХ ==========
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        servers_data = json.load(f)
else:
    servers_data = {server: "" for server in SERVERS}
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(servers_data, f, ensure_ascii=False, indent=2)

def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(servers_data, f, ensure_ascii=False, indent=2)

# ========== ФОРМАТИРОВАНИЕ СПИСКА ==========
def format_list():
    lines = []
    for server in SERVERS:
        lines.append(server)
        if servers_data.get(server):
            lines.append(f"  • {servers_data[server]}")
        lines.append("")
    return '\n'.join(lines)

# ========== ПОИСК СЕРВЕРА ПО НАЗВАНИЮ ==========
def find_server(query):
    query = query.upper()
    
    # Сначала проверяем синонимы
    if query in SYNONYMS:
        query = SYNONYMS[query]
    
    # Ищем в списке серверов
    for server in SERVERS:
        # Берем название без эмодзи
        server_name = server.split(' ')[1].upper() if ' ' in server else server.upper()
        if query == server_name or query in server_name:
            return server
    return None

# ========== КОМАНДЫ ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Чтобы записать слет:\n"
        "/i НАЗВАНИЕ_СЕРВЕРА ТЕКСТ\n"
        "Примеры:\n"
        "/i блу тест 123\n"
        "/i москва кор 20\n"
        "/i вайт подъезд 22:30"
    )

async def add_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("❓ Нужно указать сервер и текст")
        return
    
    query = context.args[0]
    text = ' '.join(context.args[1:])
    
    server = find_server(query)
    
    if not server:
        await update.message.reply_text("❌ Сервер не найден")
        return
    
    servers_data[server] = text
    save_data()
    
    await update.message.reply_text(f"✅ Записано на {server}: {text}")

async def list_entries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(format_list())

async def clear_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Только для владельца")
        return
    
    for server in SERVERS:
        servers_data[server] = ""
    save_data()
    await update.message.reply_text("🗑 Все записи удалены")

# ========== Flask ==========
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is running!"

@app_flask.route('/health')
def health():
    return "OK"

# ========== ЗАПУСК БОТА ==========
def run_bot():
    logging.basicConfig(level=logging.INFO)
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("i", add_entry))
    app.add_handler(CommandHandler("list", list_entries))
    app.add_handler(CommandHandler("clear", clear_data))
    
    logging.info("🚀 Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    # Запускаем бота в фоне
    thread = threading.Thread(target=run_bot)
    thread.daemon = True
    thread.start()
    
    # Запускаем Flask
    port = int(os.environ.get("PORT", 8000))
    app_flask.run(host="0.0.0.0", port=port)

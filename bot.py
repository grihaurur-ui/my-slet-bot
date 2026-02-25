import json
import logging
import datetime
import os
import threading
import unidecode
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ========== НАСТРОЙКИ ==========
TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = int(os.environ.get("CHAT_ID", "0"))
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
DATA_FILE = "data.json"
MESSAGE_ID_FILE = "message_id.txt"

# ========== СПИСОК СЕРВЕРОВ ==========
SERVERS_TEXT = """
🎉 NORILSK
🦈 𝙲𝙷𝙴𝚁𝙴𝙿𝙾𝚅𝙴𝚃𝚂
💨 𝙼𝙰𝙶𝙰𝙳𝙰𝙽
🏰 𝙿𝙾𝙳𝙾L𝚂𝙺
🏙 𝚂𝚄𝚁𝙶𝚄𝚃
🏍 𝙸𝚉𝙷𝙴𝚅𝚂𝙺
🎄 𝚃𝙾𝙼𝚂𝙺
🐿 𝚃𝚅𝙴𝚁
🐦‍🔥 𝚅𝙾L𝙾𝙶𝙳𝙰
🦁 𝚃𝙰𝙶𝙰𝙽𝚁𝙾𝙶
🌼 𝙽𝙾𝚅𝙶𝙾𝚁𝙾𝙳
🫐 𝙺𝙰L𝚄𝙶𝙰
😹 𝚅L𝙰𝙳𝙸𝙼𝙸R
🐲 𝙺O𝚂𝚃𝚁𝙾𝙼𝙰
🦎 𝙲𝙷𝙸𝚃𝙰
🧣 𝙰𝚂𝚃𝚁𝙰𝙺𝙷𝙰𝙽
👜 𝙱𝚁𝙰𝚃𝚂𝙺
🥐 𝚃𝙰𝙼𝙱𝙾𝚅
🥽 𝚈𝙺𝚄𝚃𝚂𝙺
🍭 𝚄L𝚈𝙰𝙽𝙾V𝚂𝙺
🎈 𝙻𝙸𝙿𝙴𝚃𝚂𝙺
💦 𝙱𝙰𝚁𝙽𝙰𝚄L
🏛 𝚈𝙰R𝙾𝚂L𝙰𝚅L
🦅 𝙾𝚁𝙴L
🧸 𝙱𝚁𝙰𝚈́𝙽𝚂𝙺
🪭 𝙿𝚂𝙺𝙾𝚅
🫚 𝚂𝙼𝙾L𝙴𝙽𝚂𝙺
🪼 𝚂𝚃𝙰𝚅𝚁𝙾𝙿𝙾L
🪅 𝙸𝚅𝙰𝙽𝙾𝚅𝙾
🪸 𝚃𝙾L𝚈𝙰𝚃𝚃𝙸
🐋 𝚃𝚈𝙼𝙴𝙽
🌺 𝙺𝙴𝙼𝙴𝚁𝙾𝚅𝙾
🔫 𝙺𝙸𝚁𝙾𝚅
🍖 𝙾𝚁𝙴𝙽𝙱𝚄𝚁𝙶
🥋 𝙰𝚁𝙺𝙷𝙰𝙽𝙶𝙴L𝚂𝙺
🃏 𝙺𝚄𝚁𝚂𝙺
🎳 𝙼𝚄𝚁𝙼𝙰𝙽𝚂𝙺
🎷 𝙿𝙴𝙽𝚉𝙰
🎭 𝚁𝚈𝙰𝚉𝙰𝙽
⛳ 𝚃𝚄L𝙰
🏟 𝙿𝙴𝚁𝙼
🐨 𝙺𝙷𝙰𝙱𝙰𝚁𝙾𝚅𝚂𝙺
🪄 𝙲𝙷𝙴𝙱𝙾𝙺𝚂𝙰𝚁𝚈
🖇 𝙺𝚁𝙰𝚂𝙽𝙾𝚈𝙰𝚁𝚂𝙺
🕊 𝙲𝙷𝙴L𝚈𝙰𝙱𝙸𝙽𝚂𝙺
👒 𝙺𝙰L𝙸𝙽G𝚁𝙰𝙳
🧶 𝚅L𝙰D𝙸𝚅O𝚂TᴏK
🌂 𝚅L𝙰D𝙸𝙺𝙰𝚅𝙺𝙰𝚉
⛑️ 𝙼𝙰𝙺𝙷𝙰C𝙷𝙺𝙰L𝙰
🎓 𝙱𝙴L𝙶O𝚁𝙾𝙳
👑 𝚅𝙾𝚁𝙾𝙽𝙴𝚉𝙷
🎒 𝚅𝙾L𝙶𝙾G𝚁𝙰𝙳
🌪 𝙸𝚁𝙺𝚄𝚃𝚂𝙺
🪙 𝙾𝙼𝚂𝙺
🐉 𝚂𝙰𝚁𝙰T𝙾𝚅
🍙 𝙶𝚁𝙾𝚉𝙽𝚈
🍃 𝙽𝙾𝚅𝙾𝚂𝙸𝙱
🪿 𝙰𝚁𝚉𝙰𝙼𝙰𝚂
🪻 𝙺𝚁𝙰𝚂𝙽𝙾𝙳𝙰𝚁
📗 𝙴𝙺𝙱
🪺 𝙰𝙽𝙰𝙿𝙰
🍺 𝚁𝙾𝚂T𝙾𝚅
🎧 𝚂𝙰𝙼𝙰𝚁𝙰
🏛 𝙺𝙰𝚉𝙰𝙽
🌊 𝚂𝙾𝙲𝙷𝙸
🌪 𝚄𝙵𝙰
🌉 𝚂𝙿𝙱
🌇 𝙼𝙾𝚂𝙺𝙾𝚆
🤎 𝙲𝙽𝙾𝙲𝙾
📕 𝙲𝙷𝙸𝙻𝙻𝙸
❄ 𝙻𝙲𝙴
📓 𝙶𝚁𝙰𝚈
📘 𝙰𝚀𝚄𝙰
🩶 𝙿𝙻𝙰𝚃𝙸𝙽𝚄𝙼
💙 𝙰𝚀𝚄𝚁𝙴
💛 𝙶𝙾𝙻𝙳
❤‍🔥 𝙲𝚁𝙸𝙼𝚂𝙾𝙽
🩷 𝙼𝙰𝙶𝙴𝙽𝚃𝙰
🤍 𝚆𝙷𝙸𝚃𝙴
💜 𝙸𝙽𝙳𝙸𝙶𝙾
🖤 𝙱𝙻𝙰𝙲𝙺
🍒 𝙲𝙷𝙴𝚁𝚁𝚈
💕 𝙿𝙸𝙽𝙺
🍋 𝙻𝙸𝙼𝙴
💜 𝙿𝚄𝚁𝙿𝙻𝙴
🧡 𝙾𝚁𝙰𝙽𝙶𝙴
💛 𝚈𝙴L𝙻𝙾𝙼
💙 𝙱𝙻𝚄𝙴
💚 𝙶𝚁𝙴𝙴𝙽
❤ 𝚁𝙴𝙳
"""

# ========== ПАРСИНГ ==========
def parse_servers(text):
    servers = {}
    lines = text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split(' ', 1)
        if len(parts) != 2:
            continue
        emoji, name_display = parts
        name_display = name_display.strip()
        name_key = unidecode.unidecode(name_display).upper().strip()
        servers[name_key] = {
            'display': f"{emoji} {name_display}",
            'entry': ""
        }
    return servers

# ========== ЗАГРУЗКА ==========
if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
        
        servers_data = {}
        for key, value in old_data.items():
            if isinstance(value, dict):
                servers_data[key] = {
                    'display': value.get('display', key),
                    'entry': value.get('entry', '')
                }
            else:
                servers_data = parse_servers(SERVERS_TEXT)
                break
    except:
        servers_data = parse_servers(SERVERS_TEXT)
else:
    servers_data = parse_servers(SERVERS_TEXT)

def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(servers_data, f, ensure_ascii=False, indent=2)

save_data()

# ========== РАБОТА С ID СООБЩЕНИЯ ==========
def save_message_id(message_id):
    with open(MESSAGE_ID_FILE, 'w') as f:
        f.write(str(message_id))

def load_message_id():
    if os.path.exists(MESSAGE_ID_FILE):
        with open(MESSAGE_ID_FILE, 'r') as f:
            return int(f.read().strip())
    return None

# ========== ФУНКЦИЯ ФОРМИРОВАНИЯ СПИСКА ==========
def format_list():
    lines = []
    for server in servers_data.values():
        lines.append(f"{server['display']}")
        if server.get('entry'):
            lines.append(f"• {server['entry']}")
        lines.append("")
    return '\n'.join(lines)

# ========== ФУНКЦИЯ ОБНОВЛЕНИЯ СООБЩЕНИЯ ==========
async def update_list_message(context):
    message_id = load_message_id()
    if message_id is None:
        sent_message = await context.bot.send_message(chat_id=CHAT_ID, text=format_list())
        save_message_id(sent_message.message_id)
        try:
            await context.bot.pin_chat_message(chat_id=CHAT_ID, message_id=sent_message.message_id)
        except:
            pass
    else:
        try:
            await context.bot.edit_message_text(
                chat_id=CHAT_ID,
                message_id=message_id,
                text=format_list()
            )
        except Exception as e:
            print(f"Error editing message: {e}")
            sent_message = await context.bot.send_message(chat_id=CHAT_ID, text=format_list())
            save_message_id(sent_message.message_id)
            try:
                await context.bot.pin_chat_message(chat_id=CHAT_ID, message_id=sent_message.message_id)
            except:
                pass

# ========== СИНОНИМЫ ==========
SYNONYMS = {
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
    "МОСКВА": "MOSCOW",
    "ПИТЕР": "SPB", "СПБ": "SPB", "САНКТ-ПЕТЕРБУРГ": "SPB",
    "КАЗАНЬ": "KAZAN",
    "ЕКБ": "EKB", "ЕКАТЕРИНБУРГ": "EKB",
    "НОВОСИБ": "NOVOSIB", "НОВОСИБИРСК": "NOVOSIB",
}

# ========== КОМАНДЫ БОТА ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Чтобы записать слет /i (сервер)\n"
        "пример /i блу бусс 22 или /i москва кор 20"
    )
    await update_list_message(context)

async def add_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text(
            "❓ Нужно указать сервер и текст слёта.\n"
            "Пример: /i блу рубль 15"
        )
        return

    server_input = context.args[0].upper()
    
    if server_input in SYNONYMS:
        server_input = SYNONYMS[server_input]

    if server_input not in servers_data:
        matches = [key for key in servers_data if server_input in key]
        if matches:
            suggestions = ', '.join([servers_data[m]['display'] for m in matches[:3]])
            await update.message.reply_text(f"❌ Сервер не найден. Возможно, вы имели в виду:\n{suggestions}")
        else:
            await update.message.reply_text("❌ Такой сервер не найден.")
        return

    entry_text = ' '.join(context.args[1:])
    
    servers_data[server_input]['entry'] = entry_text
    save_data()
    
    await update.message.reply_text(
        f"✅ Запись добавлена на {servers_data[server_input]['display']}: {entry_text}"
    )

    await update_list_message(context)

async def list_entries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(format_list())

async def clear_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Эта команда только для владельца.")
        return
    for server in servers_data.values():
        server['entry'] = ""
    save_data()
    await update.message.reply_text("🗑 Все записи удалены.")
    await update_list_message(context)

# ========== Flask для Health Check ==========
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is running!"

@app_flask.route('/health')
def health():
    return "OK", 200

# ========== ЗАПУСК БОТА ==========
def run_bot():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
        level=logging.INFO
    )
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("i", add_entry))
    app.add_handler(CommandHandler("list", list_entries))
    app.add_handler(CommandHandler("clear", clear_data))
    
    logging.info("🚀 Бот запущен...")
    app.run_polling(drop_pending_updates=True)

# ========== ТОЧКА ВХОДА ==========
if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    port = int(os.environ.get("PORT", 8000))
    app_flask.run(host="0.0.0.0", port=port)

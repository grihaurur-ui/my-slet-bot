import json
import logging
import os
import asyncio
import datetime
from collections import deque
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ========== НАСТРОЙКИ ==========
TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = int(os.environ.get("CHAT_ID", "0"))
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
DATA_FILE = "data.json"
MESSAGE_ID_FILE = "message_id.txt"
LOG_FILE = "logs.json"
MAX_LOGS = 100

# ========== ТВОЙ ПОЛНЫЙ СПИСОК СЕРВЕРОВ ==========
SERVERS = [
    "🎉 NORILSK", "🦈 CHEREPOVETS", "💨 MAGADAN", "🏰 PODOLSK", "🏙 SURGUT",
    "🏍 IZHEVSK", "🎄 TOMSK", "🐿 TVER", "🐦‍🔥 VOLOGDA", "🦁 TAGANROG",
    "🌼 NOVGOROD", "🫐 KALUGA", "😹 VLADIMIR", "🐲 KOSTROMA", "🦎 CHITA",
    "🧣 ASTRAKHAN", "👜 BRATSK", "🥐 TAMBOV", "🥽 YAKUTSK", "🍭 ULYANOVSK",
    "🎈 LIPETSK", "💦 BARNAUL", "🏛 YAROSLAVL", "🦅 OREL", "🧸 BRYANSK",
    "🪭 PSKOV", "🫚 SMOLENSK", "🪼 STAVROPOL", "🪅 IVANOVO", "🪸 TOLYATTI",
    "🐋 TYUMEN", "🌺 KEMEROVO", "🔫 KIROV", "🍖 ORENBURG", "🥋 ARKHANGELSK",
    "🃏 KURSK", "🎳 MURMANSK", "🎷 PENZA", "🎭 RYAZAN", "⛳ TULA",
    "🏟 PERM", "🐨 KHABAROVSK", "🪄 CHEBOKSARY", "🖇 KRASNOYARSK", "🕊 CHELYABINSK",
    "👒 KALININGRAD", "🧶 VLADIVOSTOK", "🌂 VLADIKAVKAZ", "⛑️ MAKHACHKALA", "🎓 BELGOROD",
    "👑 VORONEZH", "🎒 VOLGOGRAD", "🌪 IRKUTSK", "🪙 OMSK", "🐉 SARATOV",
    "🍙 GROZNY", "🍃 NOVOSIB", "🪿 ARZAMAS", "🪻 KRASNODAR", "📗 EKB",
    "🪺 ANAPA", "🍺 ROSTOV", "🎧 SAMARA", "🏛 KAZAN", "🌊 SOCHI",
    "🌪 UFA", "🌉 SPB", "🌇 MOSCOW", "🤎 COCO", "📕 CHILLI",
    "❄ LCE", "📓 GRAY", "📘 AQUA", "🩶 PLATINUM", "💙 AQURE",
    "💛 GOLD", "❤‍🔥 CRIMSON", "🩷 MAGENTA", "🤍 WHITE", "💜 INDIGO",
    "🖤 BLACK", "🍒 CHERRY", "💕 PINK", "🍋 LIME", "💜 PURPLE",
    "🧡 ORANGE", "💛 YELLOW", "💙 BLUE", "💚 GREEN", "❤ RED"
]

# ========== РАСШИРЕННЫЕ СИНОНИМЫ ==========
SYNONYMS = {
    # WHITE - все варианты
    "ВАЙТ": "WHITE", "БЕЛЫЙ": "WHITE", "ВЙТ": "WHITE", "УАЙТ": "WHITE",
    
    # BLUE - все варианты
    "БЛУ": "BLUE", "СИНИЙ": "BLUE", "БЛЮ": "BLUE", "БЛУУ": "BLUE",
    
    # GREEN - все варианты
    "ГРИН": "GREEN", "ЗЕЛЕНЫЙ": "GREEN", "ГРИН": "GREEN", "ГРИНН": "GREEN",
    
    # GOLD - все варианты
    "ГОЛД": "GOLD", "ЗОЛОТО": "GOLD", "ГОЛД": "GOLD", "ГОЛДД": "GOLD",
    
    # PINK - все варианты
    "ПИНК": "PINK", "РОЗОВЫЙ": "PINK", "ПИНК": "PINK", "ПИНКК": "PINK",
    
    # BLACK - все варианты (ИСПРАВЛЕНО: блек, блэк, блэack)
    "БЛЭК": "BLACK", "ЧЕРНЫЙ": "BLACK", "БЛЕК": "BLACK", "БЛЭКК": "BLACK", "БЛЭК": "BLACK", "БЛЭКК": "BLACK",
    
    # RED - все варианты
    "РЭД": "RED", "РЕД": "RED", "КРАСНЫЙ": "RED", "РЭДД": "RED", "РЕДД": "RED",
    
    # ORANGE - все варианты
    "ОРАНЖ": "ORANGE", "ОРАНЖЕВЫЙ": "ORANGE", "ОРАНЖ": "ORANGE", "ОРАНЖЖ": "ORANGE",
    
    # PURPLE - все варианты
    "ПЁРПЛ": "PURPLE", "ПУРПЛ": "PURPLE", "ФИОЛЕТОВЫЙ": "PURPLE", "ПУРПУР": "PURPLE", "ПЁРПЛ": "PURPLE",
    
    # LIME - все варианты
    "ЛАЙМ": "LIME", "ЛАЙМ": "LIME", "ЛАЙММ": "LIME",
    
    # CHERRY - все варианты
    "ЧЕРРИ": "CHERRY", "ВИШНЯ": "CHERRY", "ЧЕРИ": "CHERRY", "ЧЕРРИ": "CHERRY",
    
    # INDIGO - все варианты
    "ИНДИГО": "INDIGO", "ИНДИГО": "INDIGO",
    
    # MAGENTA - все варианты
    "МАДЖЕНТА": "MAGENTA", "МАДЖЕНТА": "MAGENTA", "МАДЖЕНТТА": "MAGENTA",
    
    # CRIMSON - все варианты
    "КРИМСОН": "CRIMSON", "КРИМЗОН": "CRIMSON", "КРИМСОН": "CRIMSON",
    
    # AQUA - все варианты
    "АКВА": "AQUA", "АКВА": "AQUA", "АКВВА": "AQUA",
    
    # GRAY - все варианты
    "ГРЕЙ": "GRAY", "СЕРЫЙ": "GRAY", "ГРЭЙ": "GRAY", "ГРЕЙ": "GRAY",
    
    # LCE - все варианты
    "ЛЦЕ": "LCE", "ЛСЕ": "LCE", "ЛЦЕ": "LCE",
    
    # CHILLI - все варианты
    "ЧИЛЛИ": "CHILLI", "ЧИЛИ": "CHILLI", "ЧИЛЛИ": "CHILLI",
    
    # COCO - все варианты
    "КОКО": "COCO", "КОКО": "COCO",
    
    # PLATINUM - все варианты
    "ПЛАТИНУМ": "PLATINUM", "ПЛАТИНА": "PLATINUM", "ПЛАТИНУМ": "PLATINUM",
    
    # AQURE - все варианты
    "АКУРЕ": "AQURE", "АКУРЭ": "AQURE", "АКУРЕ": "AQURE",
    
    # Города (русские названия) с вариантами
    "МОСКВА": "MOSCOW", "МСК": "MOSCOW",
    "ПИТЕР": "SPB", "СПБ": "SPB", "САНКТ-ПЕТЕРБУРГ": "SPB", "ЛЕНИНГРАД": "SPB",
    "КАЗАНЬ": "KAZAN", "КАЗАН": "KAZAN",
    "ЕКБ": "EKB", "ЕКАТЕРИНБУРГ": "EKB", "ЕКБ": "EKB",
    "НОВОСИБ": "NOVOSIB", "НОВОСИБИРСК": "NOVOSIB", "НОВОСИБ": "NOVOSIB",
    "КРАСНОДАР": "KRASNODAR", "КРД": "KRASNODAR",
    "СОЧИ": "SOCHI", "СОЧИ": "SOCHI",
    "УФА": "UFA", "УФА": "UFA",
    "РОСТОВ": "ROSTOV", "РОСТОВ-НА-ДОНУ": "ROSTOV", "РНД": "ROSTOV",
    "САМАРА": "SAMARA", "САМАРА": "SAMARA",
    "НИЖНИЙ НОВГОРОД": "NOVGOROD", "НН": "NOVGOROD", "НИЖНИЙ": "NOVGOROD",
    "НОРИЛЬСК": "NORILSK", "НОРИЛЬСК": "NORILSK",
    "ЧЕРЕПОВЕЦ": "CHEREPOVETS", "ЧЕРЕПОВЕЦ": "CHEREPOVETS",
    "МАГАДАН": "MAGADAN", "МАГАДАН": "MAGADAN",
    "ПОДОЛЬСК": "PODOLSK", "ПОДОЛЬСК": "PODOLSK",
    "СУРГУТ": "SURGUT", "СУРГУТ": "SURGUT",
    "ИЖЕВСК": "IZHEVSK", "ИЖЕВСК": "IZHEVSK",
    "ТОМСК": "TOMSK", "ТОМСК": "TOMSK",
    "ТВЕРЬ": "TVER", "ТВЕРЬ": "TVER",
    "ВОЛОГДА": "VOLOGDA", "ВОЛОГДА": "VOLOGDA",
    "ТАГАНРОГ": "TAGANROG", "ТАГАНРОГ": "TAGANROG",
    "НОВГОРОД": "NOVGOROD", "ВЕЛИКИЙ НОВГОРОД": "NOVGOROD",
    "КАЛУГА": "KALUGA", "КАЛУГА": "KALUGA",
    "ВЛАДИМИР": "VLADIMIR", "ВЛАДИМИР": "VLADIMIR",
    "КОСТРОМА": "KOSTROMA", "КОСТРОМА": "KOSTROMA",
    "ЧИТА": "CHITA", "ЧИТА": "CHITA",
    "АСТРАХАНЬ": "ASTRAKHAN", "АСТРАХАНЬ": "ASTRAKHAN",
    "БРАТСК": "BRATSK", "БРАТСК": "BRATSK",
    "ТАМБОВ": "TAMBOV", "ТАМБОВ": "TAMBOV",
    "ЯКУТСК": "YAKUTSK", "ЯКУТСК": "YAKUTSK",
    "УЛЬЯНОВСК": "ULYANOVSK", "УЛЬЯНОВСК": "ULYANOVSK",
    "ЛИПЕЦК": "LIPETSK", "ЛИПЕЦК": "LIPETSK",
    "БАРНАУЛ": "BARNAUL", "БАРНАУЛ": "BARNAUL",
    "ЯРОСЛАВЛЬ": "YAROSLAVL", "ЯРОСЛАВЛЬ": "YAROSLAVL",
    "ОРЕЛ": "OREL", "ОРЁЛ": "OREL",
    "БРЯНСК": "BRYANSK", "БРЯНСК": "BRYANSK",
    "ПСКОВ": "PSKOV", "ПСКОВ": "PSKOV",
    "СМОЛЕНСК": "SMOLENSK", "СМОЛЕНСК": "SMOLENSK",
    "СТАВРОПОЛЬ": "STAVROPOL", "СТАВРОПОЛЬ": "STAVROPOL",
    "ИВАНОВО": "IVANOVO", "ИВАНОВО": "IVANOVO",
    "ТОЛЬЯТТИ": "TOLYATTI", "ТОЛЬЯТТИ": "TOLYATTI",
    "ТЮМЕНЬ": "TYUMEN", "ТЮМЕНЬ": "TYUMEN",
    "КЕМЕРОВО": "KEMEROVO", "КЕМЕРОВО": "KEMEROVO",
    "КИРОВ": "KIROV", "КИРОВ": "KIROV",
    "ОРЕНБУРГ": "ORENBURG", "ОРЕНБУРГ": "ORENBURG",
    "АРХАНГЕЛЬСК": "ARKHANGELSK", "АРХАНГЕЛЬСК": "ARKHANGELSK",
    "КУРСК": "KURSK", "КУРСК": "KURSK",
    "МУРМАНСК": "MURMANSK", "МУРМАНСК": "MURMANSK",
    "ПЕНЗА": "PENZA", "ПЕНЗА": "PENZA",
    "РЯЗАНЬ": "RYAZAN", "РЯЗАНЬ": "RYAZAN",
    "ТУЛА": "TULA", "ТУЛА": "TULA",
    "ПЕРМЬ": "PERM", "ПЕРМЬ": "PERM",
    "ХАБАРОВСК": "KHABAROVSK", "ХАБАРОВСК": "KHABAROVSK",
    "ЧЕБОКСАРЫ": "CHEBOKSARY", "ЧЕБОКСАРЫ": "CHEBOKSARY",
    "КРАСНОЯРСК": "KRASNOYARSK", "КРАСНОЯРСК": "KRASNOYARSK",
    "ЧЕЛЯБИНСК": "CHELYABINSK", "ЧЕЛЯБИНСК": "CHELYABINSK",
    "КАЛИНИНГРАД": "KALININGRAD", "КАЛИНИНГРАД": "KALININGRAD",
    "ВЛАДИВОСТОК": "VLADIVOSTOK", "ВЛАДИВОСТОК": "VLADIVOSTOK",
    "ВЛАДИКАВКАЗ": "VLADIKAVKAZ", "ВЛАДИКАВКАЗ": "VLADIKAVKAZ",
    "МАХАЧКАЛА": "MAKHACHKALA", "МАХАЧКАЛА": "MAKHACHKALA",
    "БЕЛГОРОД": "BELGOROD", "БЕЛГОРОД": "BELGOROD",
    "ВОРОНЕЖ": "VORONEZH", "ВОРОНЕЖ": "VORONEZH",
    "ВОЛГОГРАД": "VOLGOGRAD", "ВОЛГОГРАД": "VOLGOGRAD",
    "ИРКУТСК": "IRKUTSK", "ИРКУТСК": "IRKUTSK",
    "ОМСК": "OMSK", "ОМСК": "OMSK",
    "САРАТОВ": "SARATOV", "САРАТОВ": "SARATOV",
    "ГРОЗНЫЙ": "GROZNY", "ГРОЗНЫЙ": "GROZNY",
    "АРЗАМАС": "ARZAMAS", "АРЗАМАС": "ARZAMAS",
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

# ========== ЛОГИРОВАНИЕ ==========
def load_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_logs(logs):
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

def add_log(user_id, user_name, action, details):
    logs = load_logs()
    log_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": user_id,
        "user_name": user_name,
        "action": action,
        "details": details
    }
    logs.append(log_entry)
    if len(logs) > MAX_LOGS:
        logs = logs[-MAX_LOGS:]
    save_logs(logs)

# ========== ФОРМАТИРОВАНИЕ СПИСКА ==========
def format_list():
    lines = []
    for server in SERVERS:
        if servers_data.get(server):
            lines.append(f"{server}  • {servers_data[server]}")
        else:
            lines.append(server)
    return '\n'.join(lines)

# ========== ПОИСК СЕРВЕРА ==========
def find_server(query):
    query = query.upper().strip()
    if query in SYNONYMS:
        query = SYNONYMS[query]
    for server in SERVERS:
        server_name = server.split(' ')[1].upper() if ' ' in server else server.upper()
        if query == server_name:
            return server
    for server in SERVERS:
        server_name = server.split(' ')[1].upper() if ' ' in server else server.upper()
        if query in server_name or server_name in query:
            return server
    return None

# ========== РАБОТА С ID СООБЩЕНИЯ ==========
def save_message_id(message_id):
    with open(MESSAGE_ID_FILE, 'w') as f:
        f.write(str(message_id))

def load_message_id():
    if os.path.exists(MESSAGE_ID_FILE):
        with open(MESSAGE_ID_FILE, 'r') as f:
            return int(f.read().strip())
    return None

# ========== ИСПРАВЛЕННАЯ ФУНКЦИЯ ОБНОВЛЕНИЯ СПИСКА ==========
async def update_list_message(context):
    """Обновляет закреплённое сообщение со списком"""
    full_text = format_list()
    bot_username = (await context.bot.get_me()).username
    
    try:
        # Получаем информацию о чате
        chat = await context.bot.get_chat(chat_id=CHAT_ID)
        
        # Проверяем, есть ли закреплённое сообщение
        if chat.pinned_message:
            pinned_id = chat.pinned_message.message_id
            pinned_from_bot = chat.pinned_message.from_user.is_bot
            
            # Если закреплённое сообщение от бота - редактируем его
            if pinned_from_bot:
                try:
                    await context.bot.edit_message_text(
                        chat_id=CHAT_ID,
                        message_id=pinned_id,
                        text=full_text
                    )
                    save_message_id(pinned_id)
                    logging.info(f"Отредактировано закреплённое сообщение {pinned_id}")
                    return
                except Exception as e:
                    logging.warning(f"Не удалось отредактировать закреплённое: {e}")
        
        # Если закреплённого нет или оно не от бота - ищем последние сообщения бота
        async for message in context.bot.get_chat_history(chat_id=CHAT_ID, limit=10):
            if message.from_user and message.from_user.is_bot and message.from_user.username == bot_username:
                try:
                    await context.bot.edit_message_text(
                        chat_id=CHAT_ID,
                        message_id=message.message_id,
                        text=full_text
                    )
                    # Пробуем закрепить это сообщение
                    try:
                        await context.bot.pin_chat_message(
                            chat_id=CHAT_ID,
                            message_id=message.message_id,
                            disable_notification=True
                        )
                    except:
                        pass
                    save_message_id(message.message_id)
                    logging.info(f"Отредактировано и закреплено сообщение {message.message_id}")
                    return
                except:
                    pass
        
        # Если ничего не нашли - отправляем новое сообщение
        sent_message = await context.bot.send_message(chat_id=CHAT_ID, text=full_text)
        
        # Закрепляем новое сообщение
        try:
            await context.bot.pin_chat_message(
                chat_id=CHAT_ID,
                message_id=sent_message.message_id,
                disable_notification=True
            )
            logging.info(f"Отправлено и закреплено новое сообщение {sent_message.message_id}")
        except Exception as e:
            logging.warning(f"Не удалось закрепить новое сообщение: {e}")
        
        save_message_id(sent_message.message_id)
        
    except Exception as e:
        logging.error(f"Критическая ошибка в update_list_message: {e}")
        # В крайнем случае просто отправляем сообщение
        sent_message = await context.bot.send_message(chat_id=CHAT_ID, text=full_text)
        save_message_id(sent_message.message_id)

# ========== АВТОМАТИЧЕСКИЙ ПЕРЕЗАПУСК ==========
async def auto_start(context: ContextTypes.DEFAULT_TYPE):
    await start(Update(None, None), context)

# ========== КОМАНДЫ ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Чтобы записать слет:\n"
        "/i НАЗВАНИЕ_СЕРВЕРА ТЕКСТ\n\n"
        "Примеры:\n"
        "/i блу тест 123\n"
        "/i москва кор 20\n"
        "/i вайт подъезд 22:30\n\n"
        "Список обновляется в закреплённом сообщении."
    )
    await update_list_message(context)

async def add_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("❓ Нужно указать сервер и текст\nПример: /i блу тест 123")
        return
    
    query = context.args[0]
    text = ' '.join(context.args[1:])
    
    server = find_server(query)
    
    if not server:
        await update.message.reply_text("❌ Сервер не найден")
        return
    
    servers_data[server] = text
    save_data()
    
    user = update.effective_user
    user_name = user.username or user.first_name or str(user.id)
    add_log(
        user_id=user.id,
        user_name=user_name,
        action="Добавление слёта",
        details=f"{server}: {text}"
    )
    
    await update.message.reply_text(f"✅ Записано на {server}: {text}")
    await update_list_message(context)

async def list_entries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    full_list = format_list()
    if len(full_list) > 4096:
        parts = [full_list[i:i+4096] for i in range(0, len(full_list), 4096)]
        for part in parts:
            await update.message.reply_text(part)
    else:
        await update.message.reply_text(full_list)

async def clear_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Только для владельца")
        return
    
    for server in SERVERS:
        servers_data[server] = ""
    save_data()
    
    user = update.effective_user
    user_name = user.username or user.first_name or str(user.id)
    add_log(
        user_id=user.id,
        user_name=user_name,
        action="Очистка всех слётов",
        details="Полная очистка"
    )
    
    await update.message.reply_text("🗑 Все записи удалены")
    await update_list_message(context)

async def show_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Только для владельца")
        return
    
    logs = load_logs()
    if not logs:
        await update.message.reply_text("📭 Лог пуст")
        return
    
    lines = ["📋 **Последние действия:**\n"]
    for log in logs[-20:]:
        lines.append(
            f"[{log['timestamp']}] "
            f"@{log['user_name']} (ID: {log['user_id']})\n"
            f"  • {log['action']}: {log['details']}\n"
        )
    
    text = '\n'.join(lines)
    if len(text) > 4096:
        for i in range(0, len(text), 4096):
            await update.message.reply_text(text[i:i+4096])
    else:
        await update.message.reply_text(text)

async def clear_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Только для владельца")
        return
    
    save_logs([])
    await update.message.reply_text("🗑 Логи очищены")

async def new_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Только для владельца")
        return
    
    for server in SERVERS:
        servers_data[server] = ""
    save_data()
    
    if os.path.exists(MESSAGE_ID_FILE):
        os.remove(MESSAGE_ID_FILE)
    
    await update.message.reply_text("📋 Создаю новый чистый список...")
    await update_list_message(context)
    await update.message.reply_text("✅ Новый список готов и закреплён!")

# ========== Flask ==========
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is running!"

@app_flask.route('/health')
def health():
    return "OK"

# ========== ЗАПУСК ==========
async def run_bot():
    logging.basicConfig(level=logging.INFO)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("i", add_entry))
    application.add_handler(CommandHandler("list", list_entries))
    application.add_handler(CommandHandler("clear", clear_data))
    application.add_handler(CommandHandler("newlist", new_list))
    application.add_handler(CommandHandler("logs", show_logs))
    application.add_handler(CommandHandler("clear_logs", clear_logs))
    
    job_queue = application.job_queue
    if job_queue:
        job_queue.run_daily(auto_start, time=datetime.time(hour=21, minute=0, tzinfo=datetime.timezone.utc))
        job_queue.run_daily(auto_start, time=datetime.time(hour=3, minute=0, tzinfo=datetime.timezone.utc))
        logging.info("✅ Автоматический перезапуск /start запланирован на 00:00 и 06:00 МСК")
    
    logging.info("🚀 Бот запущен!")
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    import threading
    port = int(os.environ.get("PORT", 8000))
    flask_thread = threading.Thread(target=lambda: app_flask.run(host="0.0.0.0", port=port))
    flask_thread.daemon = True
    flask_thread.start()
    
    asyncio.run(run_bot())

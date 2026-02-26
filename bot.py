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
MAX_LOGS = 100  # хранить максимум 100 записей

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

# ========== ПОЛНЫЕ СИНОНИМЫ ==========
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
    "ЛАЙМ": "LIME", "ЧЕРРИ": "CHERRY", "ВИШНЯ": "CHERRY",
    "ИНДИГО": "INDIGO", "МАДЖЕНТА": "MAGENTA", "КРИМСОН": "CRIMSON",
    "АКВА": "AQUA", "ГРЕЙ": "GRAY", "СЕРЫЙ": "GRAY",
    "ЛЦЕ": "LCE", "ЧИЛЛИ": "CHILLI", "КОКО": "COCO",
    "ПЛАТИНУМ": "PLATINUM", "АКУРЕ": "AQURE",
    "МОСКВА": "MOSCOW", "ПИТЕР": "SPB", "СПБ": "SPB", "САНКТ-ПЕТЕРБУРГ": "SPB",
    "КАЗАНЬ": "KAZAN", "ЕКБ": "EKB", "ЕКАТЕРИНБУРГ": "EKB",
    "НОВОСИБ": "NOVOSIB", "НОВОСИБИРСК": "NOVOSIB",
    "КРАСНОДАР": "KRASNODAR", "СОЧИ": "SOCHI", "УФА": "UFA",
    "РОСТОВ": "ROSTOV", "САМАРА": "SAMARA", "НИЖНИЙ НОВГОРОД": "NOVGOROD", "НН": "NOVGOROD",
    "НОРИЛЬСК": "NORILSK", "ЧЕРЕПОВЕЦ": "CHEREPOVETS", "МАГАДАН": "MAGADAN",
    "ПОДОЛЬСК": "PODOLSK", "СУРГУТ": "SURGUT", "ИЖЕВСК": "IZHEVSK",
    "ТОМСК": "TOMSK", "ТВЕРЬ": "TVER", "ВОЛОГДА": "VOLOGDA",
    "ТАГАНРОГ": "TAGANROG", "НОВГОРОД": "NOVGOROD", "КАЛУГА": "KALUGA",
    "ВЛАДИМИР": "VLADIMIR", "КОСТРОМА": "KOSTROMA", "ЧИТА": "CHITA",
    "АСТРАХАНЬ": "ASTRAKHAN", "БРАТСК": "BRATSK", "ТАМБОВ": "TAMBOV",
    "ЯКУТСК": "YAKUTSK", "УЛЬЯНОВСК": "ULYANOVSK", "ЛИПЕЦК": "LIPETSK",
    "БАРНАУЛ": "BARNAUL", "ЯРОСЛАВЛЬ": "YAROSLAVL", "ОРЕЛ": "OREL",
    "БРЯНСК": "BRYANSK", "ПСКОВ": "PSKOV", "СМОЛЕНСК": "SMOLENSK",
    "СТАВРОПОЛЬ": "STAVROPOL", "ИВАНОВО": "IVANOVO", "ТОЛЬЯТТИ": "TOLYATTI",
    "ТЮМЕНЬ": "TYUMEN", "КЕМЕРОВО": "KEMEROVO", "КИРОВ": "KIROV",
    "ОРЕНБУРГ": "ORENBURG", "АРХАНГЕЛЬСК": "ARKHANGELSK", "КУРСК": "KURSK",
    "МУРМАНСК": "MURMANSK", "ПЕНЗА": "PENZA", "РЯЗАНЬ": "RYAZAN",
    "ТУЛА": "TULA", "ПЕРМЬ": "PERM", "ХАБАРОВСК": "KHABAROVSK",
    "ЧЕБОКСАРЫ": "CHEBOKSARY", "КРАСНОЯРСК": "KRASNOYARSK", "ЧЕЛЯБИНСК": "CHELYABINSK",
    "КАЛИНИНГРАД": "KALININGRAD", "ВЛАДИВОСТОК": "VLADIVOSTOK", "ВЛАДИКАВКАЗ": "VLADIKAVKAZ",
    "МАХАЧКАЛА": "MAKHACHKALA", "БЕЛГОРОД": "BELGOROD", "ВОРОНЕЖ": "VORONEZH",
    "ВОЛГОГРАД": "VOLGOGRAD", "ИРКУТСК": "IRKUTSK", "ОМСК": "OMSK",
    "САРАТОВ": "SARATOV", "ГРОЗНЫЙ": "GROZNY", "АРЗАМАС": "ARZAMAS",
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

# ========== ЛОГИРОВАНИЕ ДЕЙСТВИЙ ==========
def load_logs():
    """Загружает логи из файла"""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_logs(logs):
    """Сохраняет логи в файл"""
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

def add_log(user_id, user_name, action, details):
    """Добавляет запись в лог"""
    logs = load_logs()
    
    log_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": user_id,
        "user_name": user_name,
        "action": action,
        "details": details
    }
    
    logs.append(log_entry)
    
    # Оставляем только последние MAX_LOGS записей
    if len(logs) > MAX_LOGS:
        logs = logs[-MAX_LOGS:]
    
    save_logs(logs)

# ========== ФОРМАТИРОВАНИЕ СПИСКА (КОМПАКТНАЯ ВЕРСИЯ) ==========
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

async def update_list_message(context):
    """Обновляет одно закреплённое сообщение со списком"""
    message_id = load_message_id()
    full_text = format_list()
    
    # Если есть сохранённый ID, пробуем отредактировать
    if message_id is not None:
        try:
            await context.bot.edit_message_text(
                chat_id=CHAT_ID,
                message_id=message_id,
                text=full_text
            )
            return  # Успешно отредактировали, выходим
        except Exception as e:
            # Если не получилось отредактировать (сообщение удалено или ID неверный)
            logging.warning(f"Не удалось отредактировать сообщение {message_id}: {e}")
            # Продолжаем и создаём новое
    
    # Создаём новое сообщение
    try:
        # Сначала ищем существующее закреплённое сообщение бота
        chat = await context.bot.get_chat(chat_id=CHAT_ID)
        if chat.pinned_message and chat.pinned_message.from_user.id == context.bot.id:
            # Если есть закреплённое сообщение от бота - редактируем его
            try:
                await context.bot.edit_message_text(
                    chat_id=CHAT_ID,
                    message_id=chat.pinned_message.message_id,
                    text=full_text
                )
                save_message_id(chat.pinned_message.message_id)
                return
            except:
                pass
        
        # Если нет - отправляем новое
        sent_message = await context.bot.send_message(chat_id=CHAT_ID, text=full_text)
        save_message_id(sent_message.message_id)
        
        # Пробуем закрепить
        try:
            await context.bot.pin_chat_message(
                chat_id=CHAT_ID, 
                message_id=sent_message.message_id,
                disable_notification=True
            )
        except Exception as e:
            logging.warning(f"Не удалось закрепить сообщение: {e}")
            
    except Exception as e:
        logging.error(f"Ошибка при создании сообщения: {e}")

# ========== АВТОМАТИЧЕСКИЙ ПЕРЕЗАПУСК ==========
async def auto_start(context: ContextTypes.DEFAULT_TYPE):
    """Автоматически вызывает команду start в 00:00 и 06:00 МСК"""
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
    
    # Получаем имя пользователя
    user = update.effective_user
    user_name = user.username or user.first_name or str(user.id)
    
    # Логируем действие
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
    
    # Логируем действие
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

# ========== НОВАЯ КОМАНДА ДЛЯ ПРОСМОТРА ЛОГОВ ==========
async def show_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает последние действия (только для владельца)"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Только для владельца")
        return
    
    logs = load_logs()
    
    if not logs:
        await update.message.reply_text("📭 Лог пуст")
        return
    
    # Показываем последние 20 записей
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

# ========== КОМАНДА ДЛЯ ОЧИСТКИ ЛОГОВ ==========
async def clear_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Очищает все логи (только для владельца)"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Только для владельца")
        return
    
    save_logs([])
    await update.message.reply_text("🗑 Логи очищены")

# ========== КОМАНДА ДЛЯ НОВОГО СПИСКА ==========
async def new_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Создаёт новый чистый список (только для владельца)"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Только для владельца")
        return
    
    # Очищаем все записи
    for server in SERVERS:
        servers_data[server] = ""
    save_data()
    
    # Удаляем старый файл с ID сообщения
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
    
    # Планировщик задач
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


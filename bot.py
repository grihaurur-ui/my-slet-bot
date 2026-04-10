import json
import logging
import os
import asyncio
import datetime
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# ========== НАСТРОЙКИ ==========
TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = int(os.environ.get("CHAT_ID", "0"))
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
DATA_FILE = "data.json"
MESSAGE_ID_FILE = "message_id.txt"
LOG_FILE = "logs.json"
USERS_FILE = "users.json"
LIST_STATS_FILE = "list_stats.json"
MAX_LOGS = 1000

# ========== ТВОЙ ПОЛНЫЙ СПИСОК СЕРВЕРОВ ==========
SERVERS = [
    "🏛️ ASTANA",  # <-- НОВЫЙ ГОРОД В САМОМ ВЕРХУ
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
    "🌪 UFA", "🌉 SPB", "🌇 MOSCOW",
    "🤎 COCO", "📕 CHILLI", "❄ LCE", "📓 GRAY", "📘 AQUA", "🩶 PLATINUM", "💙 AQURE",
    "💛 GOLD", "❤‍🔥 CRIMSON", "🩷 MAGENTA", "🤍 WHITE", "💜 INDIGO", "🖤 BLACK",
    "🍒 CHERRY", "💕 PINK", "🍋 LIME", "💜 PURPLE", "🧡 ORANGE", "💛 YELLOW",
    "💙 BLUE", "💚 GREEN", "❤ RED"
]

# ========== РАСШИРЕННЫЕ СИНОНИМЫ ==========
SYNONYMS = {
    # ===== ЦВЕТА =====
    "ВАЙТ": "WHITE", "БЕЛЫЙ": "WHITE", "ВЙТ": "WHITE", "УАЙТ": "WHITE", "БЕЛ": "WHITE",
    "БЛУ": "BLUE", "СИНИЙ": "BLUE", "БЛЮ": "BLUE", "БЛУУ": "BLUE", "СИН": "BLUE",
    "ГРИН": "GREEN", "ЗЕЛЕНЫЙ": "GREEN", "ГРИНН": "GREEN", "ЗЕЛ": "GREEN", "ЗЕЛЕН": "GREEN",
    "ГОЛД": "GOLD", "ЗОЛОТО": "GOLD", "ГОЛДД": "GOLD", "ЗОЛ": "GOLD", "ЗОЛОТ": "GOLD",
    "ПИНК": "PINK", "РОЗОВЫЙ": "PINK", "ПИНКК": "PINK", "РОЗ": "PINK", "РОЗОВ": "PINK",
    "БЛЕК": "BLACK", "ЧЕРНЫЙ": "BLACK", "ЧЁРНЫЙ": "BLACK", "БЛЕКК": "BLACK", "ЧЕРН": "BLACK",
    "РЭД": "RED", "РЕД": "RED", "КРАСНЫЙ": "RED", "РЭДД": "RED", "КРАСН": "RED",
    "ОРАНЖ": "ORANGE", "ОРАНЖЕВЫЙ": "ORANGE", "ОРАНЖЖ": "ORANGE", "ОРАН": "ORANGE",
    "ПЁРПЛ": "PURPLE", "ПУРПЛ": "PURPLE", "ФИОЛЕТОВЫЙ": "PURPLE", "ПУРПУР": "PURPLE", 
    "ФИОЛ": "PURPLE", "ФИОЛЕТ": "PURPLE", "ЛИЛОВЫЙ": "PURPLE",
    "ЛАЙМ": "LIME", "ЛАЙММ": "LIME",
    "ЧЕРРИ": "CHERRY", "ВИШНЯ": "CHERRY", "ЧЕРИ": "CHERRY", "ВИШ": "CHERRY", "ВИШН": "CHERRY",
    "ИНДИГО": "INDIGO", "ИНД": "INDIGO",
    "МАДЖЕНТА": "MAGENTA", "МАДЖЕНТТА": "MAGENTA", "МАДЖ": "MAGENTA",
    "КРИМСОН": "CRIMSON", "КРИМЗОН": "CRIMSON", "КРИМ": "CRIMSON", "МАЛИНОВЫЙ": "CRIMSON",
    "АКВА": "AQUA", "АКВВА": "AQUA", "АКВ": "AQUA",
    "ГРЕЙ": "GRAY", "СЕРЫЙ": "GRAY", "ГРЭЙ": "GRAY", "СЕР": "GRAY",
    "ЛЦЕ": "LCE", "ЛСЕ": "LCE", "АЙС": "LCE", "ICE": "LCE", "ЛЁД": "LCE", "ЛЕД": "LCE",
    "ЧИЛЛИ": "CHILLI", "ЧИЛИ": "CHILLI", "ЧИЛ": "CHILLI",
    "КОКО": "COCO", "КОКОС": "COCO", "ЧОКО": "COCO", "CHOCO": "COCO", "ШОКО": "COCO",
    "ПЛАТИНУМ": "PLATINUM", "ПЛАТИНА": "PLATINUM", "ПЛАТ": "PLATINUM",
    "АКУРЕ": "AQURE", "АКУРЭ": "AQURE", "АКУР": "AQURE", "АЗУР": "AQURE", "AZUR": "AQURE",
    "ЖЕЛТЫЙ": "YELLOW", "ЖЕЛТ": "YELLOW", "ЖЁЛТЫЙ": "YELLOW", "ЕЛЛОУ": "YELLOW", "YELLOW": "YELLOW",

    # ===== ГОРОДА =====
    "МОСКВА": "MOSCOW", "МСК": "MOSCOW", "МОС": "MOSCOW", "МО": "MOSCOW",
    "ПИТЕР": "SPB", "СПБ": "SPB", "САНКТ-ПЕТЕРБУРГ": "SPB", "ЛЕНИНГРАД": "SPB", 
    "ПЕТЕРБУРГ": "SPB", "ЛЕГ": "SPB", "СП": "SPB",
    "КАЗАНЬ": "KAZAN", "КАЗАН": "KAZAN", "КАЗ": "KAZAN", "КЗН": "KAZAN",
    "ЕКБ": "EKB", "ЕКАТЕРИНБУРГ": "EKB", "ЕКАТ": "EKB", "ЕКА": "EKB",
    "НОВОСИБ": "NOVOSIB", "НОВОСИБИРСК": "NOVOSIB", "НОВОС": "NOVOSIB", "НСК": "NOVOSIB",
    "КРАСНОДАР": "KRASNODAR", "КРД": "KRASNODAR", "КРАСНО": "KRASNODAR",
    "СОЧИ": "SOCHI", "СОЧ": "SOCHI",
    "УФА": "UFA", "УФ": "UFA",
    "РОСТОВ": "ROSTOV", "РОСТОВ-НА-ДОНУ": "ROSTOV", "РНД": "ROSTOV", "РОСТ": "ROSTOV",
    "САМАРА": "SAMARA", "САМ": "SAMARA", "САМА": "SAMARA", "СМР": "SAMARA",
    "НИЖНИЙ НОВГОРОД": "NOVGOROD", "НН": "NOVGOROD", "НИЖНИЙ": "NOVGOROD",
    "НОРИЛЬСК": "NORILSK", "НОРИЛ": "NORILSK", "НОР": "NORILSK",
    "ЧЕРЕПОВЕЦ": "CHEREPOVETS", "ЧЕРЕП": "CHEREPOVETS",
    "МАГАДАН": "MAGADAN",
    "ПОДОЛЬСК": "PODOLSK",
    "СУРГУТ": "SURGUT",
    "ИЖЕВСК": "IZHEVSK",
    "ТОМСК": "TOMSK",
    "ТВЕРЬ": "TVER",
    "ВОЛОГДА": "VOLOGDA",
    "ТАГАНРОГ": "TAGANROG",
    "НОВГОРОД": "NOVGOROD",
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
    "ОРЕЛ": "OREL", "ОРЁЛ": "OREL",
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
    "ВЛАДИВОСТОК": "VLADIVOSTOK", "ВОСТОК": "VLADIVOSTOK", "ВЛАДИК": "VLADIVOSTOK", "ВЛ": "VLADIVOSTOK",
    "ВЛАДИКАВКАЗ": "VLADIKAVKAZ", "КАВКАЗ": "VLADIKAVKAZ", "ВЛАДИК": "VLADIKAVKAZ", "ВЛК": "VLADIKAVKAZ",
    "МАХАЧКАЛА": "MAKHACHKALA", "МХЧ": "MAKHACHKALA",
    "БЕЛГОРОД": "BELGOROD",
    "ВОРОНЕЖ": "VORONEZH",
    "ВОЛГОГРАД": "VOLGOGRAD",
    "ИРКУТСК": "IRKUTSK",
    "ОМСК": "OMSK",
    "САРАТОВ": "SARATOV",
    "ГРОЗНЫЙ": "GROZNY",
    "АРЗАМАС": "ARZAMAS",
    "АНАПА": "ANAPA", "АНП": "ANAPA",
    # ===== НОВЫЙ ГОРОД =====
"АСТАНА": "ASTANA", "АСТА": "ASTANA", "ASTANA": "ASTANA", "АСТ": "ASTANA",

# ===== ДОПОЛНИТЕЛЬНЫЕ СИНОНИМЫ =====
"ТЛТ": "TOLYATTI",
"ГРЗ": "GROZNY",
"ИРКА": "IRKUTSK",
"ИРК": "IRKUTSK",  # уже был, но продублирую для уверенности
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

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_user(user):
    users = load_users()
    user_id = str(user.id)
    
    users[user_id] = {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "last_seen": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def load_list_stats():
    if os.path.exists(LIST_STATS_FILE):
        with open(LIST_STATS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "created_at": None,
        "created_by": None,
        "active_users": [],
        "entries_count": 0
    }

def save_list_stats(stats):
    with open(LIST_STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

def reset_list_stats(creator_id=None):
    stats = {
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "created_by": creator_id,
        "active_users": [],
        "entries_count": 0
    }
    save_list_stats(stats)
    return stats

def add_to_list_stats(user_id):
    stats = load_list_stats()
    if user_id not in stats["active_users"]:
        stats["active_users"].append(user_id)
    stats["entries_count"] += 1
    save_list_stats(stats)

async def check_private_access(update: Update):
    if update.message.chat.type != "private":
        return True
    if update.effective_user.id == OWNER_ID:
        return True
    await update.message.reply_text("⛔ Бот доступен только в группе")
    return False

# ========== ОБНОВЛЕННАЯ ФУНКЦИЯ ФОРМАТИРОВАНИЯ СПИСКА ==========
def format_list():
    lines = []
    for server in SERVERS:
        if servers_data.get(server):
            lines.append(f"{server} - {servers_data[server]}")
        else:
            lines.append(server)
    return '\n'.join(lines)

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

def save_message_id(message_id):
    with open(MESSAGE_ID_FILE, 'w') as f:
        f.write(str(message_id))

def load_message_id():
    if os.path.exists(MESSAGE_ID_FILE):
        with open(MESSAGE_ID_FILE, 'r') as f:
            return int(f.read().strip())
    return None

async def update_list_message(context):
    full_text = format_list()
    current_message_id = load_message_id()
    
    try:
        if current_message_id:
            try:
                await context.bot.edit_message_text(
                    chat_id=CHAT_ID,
                    message_id=current_message_id,
                    text=full_text
                )
                return
            except Exception as e:
                error_str = str(e)
                if "Message is not modified" in error_str:
                    return
                elif "Message can't be edited" in error_str or "message to edit not found" in error_str.lower():
                    pass
                else:
                    logging.warning(f"⚠️ {error_str}")
        
        chat = await context.bot.get_chat(chat_id=CHAT_ID)
        
        if chat.pinned_message:
            try:
                await context.bot.edit_message_text(
                    chat_id=CHAT_ID,
                    message_id=chat.pinned_message.message_id,
                    text=full_text
                )
                save_message_id(chat.pinned_message.message_id)
                return
            except Exception as e:
                if "Message is not modified" in str(e):
                    save_message_id(chat.pinned_message.message_id)
                    return
        
        sent_message = await context.bot.send_message(chat_id=CHAT_ID, text=full_text)
        
        try:
            await context.bot.pin_chat_message(
                chat_id=CHAT_ID,
                message_id=sent_message.message_id,
                disable_notification=True
            )
        except:
            pass
        
        save_message_id(sent_message.message_id)
        
    except Exception as e:
        if "Message is not modified" not in str(e):
            logging.error(f"❌ Ошибка: {e}")

async def track_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.chat.type in ["group", "supergroup"]:
        user = update.effective_user
        if user and not user.is_bot:
            save_user(user)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_private_access(update):
        return
    
    await update.message.reply_text(
        "чтобы записать слет /i (сервер/\n"
        "пример /i блу бусс 22 или /i москва кор 20"
    )
    await update_list_message(context)

async def add_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_private_access(update):
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("❓ Нужно указать сервер и текст\nПример: /i блу бусс 22")
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
    
    add_to_list_stats(user.id)
    
    await update.message.reply_text(f"✅ Записано на {server}: {text}")
    await update_list_message(context)

async def list_entries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_private_access(update):
        return
    
    full_list = format_list()
    if len(full_list) > 4096:
        for i in range(0, len(full_list), 4096):
            await update.message.reply_text(full_list[i:i+4096])
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
    for log in logs[-50:]:
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

async def new_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Только для владельца")
        return
    
    for server in SERVERS:
        servers_data[server] = ""
    save_data()
    
    if os.path.exists(MESSAGE_ID_FILE):
        os.remove(MESSAGE_ID_FILE)
    
    reset_list_stats(update.effective_user.id)
    
    await update.message.reply_text("📋 Создаю новый чистый список...")
    
    full_text = format_list()
    
    try:
        sent_message = await context.bot.send_message(chat_id=CHAT_ID, text=full_text)
        
        try:
            await context.bot.pin_chat_message(
                chat_id=CHAT_ID,
                message_id=sent_message.message_id,
                disable_notification=True
            )
            await update.message.reply_text(f"✅ Новый список создан и закреплён! Старый список остался в чате.")
        except Exception as e:
            await update.message.reply_text(f"✅ Новый список создан, но не удалось закрепить: {e}")
        
        save_message_id(sent_message.message_id)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при создании списка: {e}")

async def list_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Только для владельца")
        return
    
    stats = load_list_stats()
    all_users = load_users()
    
    if not stats.get("created_at"):
        await update.message.reply_text("📭 Статистика по текущему списку отсутствует. Создайте новый список через /newlist")
        return
    
    total_members = 0
    try:
        total_members = await context.bot.get_chat_member_count(chat_id=CHAT_ID)
    except Exception as e:
        logging.warning(f"Не удалось получить количество участников: {e}")
    
    creator_info = "Неизвестно"
    if stats["created_by"]:
        user_id_str = str(stats["created_by"])
        if user_id_str in all_users:
            user = all_users[user_id_str]
            creator_info = f"@{user['username']}" if user['username'] else user['first_name']
        else:
            creator_info = f"ID {stats['created_by']}"
    
    lines = ["📊 **Статистика текущего списка:**\n"]
    lines.append(f"📅 Создан: {stats['created_at']}")
    lines.append(f"👤 Создал: {creator_info}")
    lines.append(f"📝 Всего записей: {stats['entries_count']}")
    lines.append(f"👥 Активных пользователей: {len(stats['active_users'])}")
    
    if total_members > 0:
        lines.append(f"👥 Всего в группе: {total_members} участников")
        lines.append(f"📊 Известно пользователей: {len(all_users)}\n")
    else:
        lines.append(f"👥 Известно пользователей: {len(all_users)}\n")
    
    lines.append("✅ **Записывали в этот список:**")
    if stats['active_users']:
        active_names = []
        for user_id in stats['active_users']:
            user_id_str = str(user_id)
            if user_id_str in all_users:
                user = all_users[user_id_str]
                name = f"@{user['username']}" if user['username'] else user['first_name']
                active_names.append(name)
            else:
                active_names.append(f"ID {user_id}")
        
        for name in active_names:
            lines.append(f"  • {name}")
    else:
        lines.append("  • Пока никто не записывал")
    
    lines.append("")
    lines.append("❌ **Не записывали в этот список:**")
    inactive_users = []
    
    for user_id, user_data in all_users.items():
        user_id_int = int(user_id)
        if user_id_int != context.bot.id and user_id_int not in stats['active_users']:
            name = f"@{user_data['username']}" if user_data['username'] else user_data['first_name']
            inactive_users.append(name)
    
    if inactive_users:
        for name in inactive_users[:30]:
            lines.append(f"  • {name}")
        if len(inactive_users) > 30:
            lines.append(f"  ... и ещё {len(inactive_users) - 30} пользователей")
    else:
        lines.append("  • Все пользователи записали слёт! 🎉")
    
    text = '\n'.join(lines)
    
    if len(text) > 4096:
        for i in range(0, len(text), 4096):
            await update.message.reply_text(text[i:i+4096])
    else:
        await update.message.reply_text(text)

async def auto_newlist(context: ContextTypes.DEFAULT_TYPE):
    logging.info("🤖 Запуск автоматического создания нового списка")
    
    for server in SERVERS:
        servers_data[server] = ""
    save_data()
    
    if os.path.exists(MESSAGE_ID_FILE):
        os.remove(MESSAGE_ID_FILE)
    
    reset_list_stats(None)
    
    full_text = format_list()
    
    try:
        sent_message = await context.bot.send_message(chat_id=CHAT_ID, text=full_text)
        
        await context.bot.pin_chat_message(
            chat_id=CHAT_ID,
            message_id=sent_message.message_id,
            disable_notification=True
        )
        
        save_message_id(sent_message.message_id)
        logging.info("✅ Автоматический новый список создан и закреплён")
        
    except Exception as e:
        logging.error(f"❌ Ошибка: {e}")

app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is running!"

@app_flask.route('/health')
def health():
    return "OK"

async def run_bot():
    logging.basicConfig(level=logging.INFO)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(MessageHandler(filters.ALL, track_users), group=-1)
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("i", add_entry))
    application.add_handler(CommandHandler("list", list_entries))
    application.add_handler(CommandHandler("clear", clear_data))
    application.add_handler(CommandHandler("newlist", new_list))
    application.add_handler(CommandHandler("logs", show_logs))
    application.add_handler(CommandHandler("stats", list_stats))
    
    job_queue = application.job_queue
    if job_queue:
        job_queue.run_daily(auto_newlist, time=datetime.time(hour=21, minute=0, tzinfo=datetime.timezone.utc))
        job_queue.run_daily(auto_newlist, time=datetime.time(hour=2, minute=0, tzinfo=datetime.timezone.utc))
        logging.info("✅ Автоматический newlist запланирован на 00:00 и 05:00 МСК")
    
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

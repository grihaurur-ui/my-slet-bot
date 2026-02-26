import json
import logging
import os
import asyncio
import datetime
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

# ========== РАСШИРЕННЫЕ СИНОНИМЫ (ПОЛНАЯ ВЕРСИЯ) ==========
SYNONYMS = {
    # ===== ЦВЕТА =====
    "ВАЙТ": "WHITE", "БЕЛЫЙ": "WHITE", "ВЙТ": "WHITE", "УАЙТ": "WHITE", "УАЙТ": "WHITE",
    
    "БЛУ": "BLUE", "СИНИЙ": "BLUE", "БЛЮ": "BLUE", "БЛУУ": "BLUE", "СИН": "BLUE",
    
    "ГРИН": "GREEN", "ЗЕЛЕНЫЙ": "GREEN", "ГРИНН": "GREEN", "ЗЕЛ": "GREEN", "ЗЕЛЕН": "GREEN",
    
    "ГОЛД": "GOLD", "ЗОЛОТО": "GOLD", "ГОЛДД": "GOLD", "ЗОЛ": "GOLD", "ЗОЛОТ": "GOLD",
    
    "ПИНК": "PINK", "РОЗОВЫЙ": "PINK", "ПИНКК": "PINK", "РОЗ": "PINK", "РОЗОВ": "PINK",
    
    "БЛЕК": "BLACK", "ЧЕРНЫЙ": "BLACK", "ЧЁРНЫЙ": "BLACK", "БЛЕКК": "BLACK", "ЧЕРН": "BLACK",
    
    "РЭД": "RED", "РЕД": "RED", "КРАСНЫЙ": "RED", "РЭДД": "RED", "КРАСН": "RED", "КРАС": "RED",
    
    "ОРАНЖ": "ORANGE", "ОРАНЖЕВЫЙ": "ORANGE", "ОРАНЖЖ": "ORANGE", "ОРАН": "ORANGE",
    
    "ПЁРПЛ": "PURPLE", "ПУРПЛ": "PURPLE", "ФИОЛЕТОВЫЙ": "PURPLE", "ПУРПУР": "PURPLE", 
    "ФИОЛ": "PURPLE", "ФИОЛЕТ": "PURPLE",
    
    "ЛАЙМ": "LIME", "ЛАЙММ": "LIME", "ЛАЙМ": "LIME",
    
    "ЧЕРРИ": "CHERRY", "ВИШНЯ": "CHERRY", "ЧЕРИ": "CHERRY", "ВИШ": "CHERRY", "ВИШН": "CHERRY",
    
    "ИНДИГО": "INDIGO", "ИНД": "INDIGO",
    
    "МАДЖЕНТА": "MAGENTA", "МАДЖЕНТТА": "MAGENTA", "МАДЖ": "MAGENTA",
    
    "КРИМСОН": "CRIMSON", "КРИМЗОН": "CRIMSON", "КРИМ": "CRIMSON",
    
    "АКВА": "AQUA", "АКВВА": "AQUA", "АКВ": "AQUA",
    
    "ГРЕЙ": "GRAY", "СЕРЫЙ": "GRAY", "ГРЭЙ": "GRAY", "СЕР": "GRAY",
    
    "ЛЦЕ": "LCE", "ЛСЕ": "LCE",
    
    "ЧИЛЛИ": "CHILLI", "ЧИЛИ": "CHILLI", "ЧИЛ": "CHILLI",
    
    "КОКО": "COCO", "КОКОС": "COCO",
    
    "ПЛАТИНУМ": "PLATINUM", "ПЛАТИНА": "PLATINUM", "ПЛАТ": "PLATINUM",
    
    "АКУРЕ": "AQURE", "АКУРЭ": "AQURE", "АКУР": "AQURE",

    # ===== ГОРОДА (ПОЛНЫЙ СПИСОК) =====
    # NORILSK
    "НОРИЛЬСК": "NORILSK", "НОРИЛ": "NORILSK", "НОР": "NORILSK",
    
    # CHEREPOVETS
    "ЧЕРЕПОВЕЦ": "CHEREPOVETS", "ЧЕРЕП": "CHEREPOVETS", "ЧЕРЕПА": "CHEREPOVETS", 
    "ЧЕР": "CHEREPOVETS",
    
    # MAGADAN
    "МАГАДАН": "MAGADAN", "МАГА": "MAGADAN", "МАГ": "MAGADAN",
    
    # PODOLSK
    "ПОДОЛЬСК": "PODOLSK", "ПОДОЛ": "PODOLSK", "ПОД": "PODOLSK",
    
    # SURGUT
    "СУРГУТ": "SURGUT", "СУР": "SURGUT", "СУРГ": "SURGUT",
    
    # IZHEVSK
    "ИЖЕВСК": "IZHEVSK", "ИЖ": "IZHEVSK", "ИЖЕВ": "IZHEVSK",
    
    # TOMSK
    "ТОМСК": "TOMSK", "ТОМ": "TOMSK", "ТОМС": "TOMSK",
    
    # TVER
    "ТВЕРЬ": "TVER", "ТВЕР": "TVER", "ТВЬ": "TVER",
    
    # VOLOGDA
    "ВОЛОГДА": "VOLOGDA", "ВОЛО": "VOLOGDA", "ВОЛ": "VOLOGDA",
    
    # TAGANROG
    "ТАГАНРОГ": "TAGANROG", "ТАГАН": "TAGANROG", "ТАГ": "TAGANROG",
    
    # NOVGOROD
    "НОВГОРОД": "NOVGOROD", "НОВГОР": "NOVGOROD", "НОВ": "NOVGOROD",
    "ВЕЛИКИЙ НОВГОРОД": "NOVGOROD", "НИЖНИЙ НОВГОРОД": "NOVGOROD", "НН": "NOVGOROD",
    "НИЖНИЙ": "NOVGOROD",
    
    # KALUGA
    "КАЛУГА": "KALUGA", "КАЛ": "KALUGA", "КАЛУ": "KALUGA",
    
    # VLADIMIR
    "ВЛАДИМИР": "VLADIMIR", "ВЛАД": "VLADIMIR", "ВЛАДИ": "VLADIMIR",
    
    # KOSTROMA
    "КОСТРОМА": "KOSTROMA", "КОСТР": "KOSTROMA", "КОСТЯ": "KOSTROMA", "КОС": "KOSTROMA",
    
    # CHITA
    "ЧИТА": "CHITA", "ЧИТ": "CHITA", "ЧИТА": "CHITA",
    
    # ASTRAKHAN
    "АСТРАХАНЬ": "ASTRAKHAN", "АСТРА": "ASTRAKHAN", "АСТ": "ASTRAKHAN", "АСТР": "ASTRAKHAN",
    
    # BRATSK
    "БРАТСК": "BRATSK", "БРАТ": "BRATSK", "БРАТС": "BRATSK",
    
    # TAMBOV
    "ТАМБОВ": "TAMBOV", "ТАМ": "TAMBOV", "ТАМБ": "TAMBOV",
    
    # YAKUTSK
    "ЯКУТСК": "YAKUTSK", "ЯКУТ": "YAKUTSK", "ЯК": "YAKUTSK",
    
    # ULYANOVSK
    "УЛЬЯНОВСК": "ULYANOVSK", "УЛЬЯ": "ULYANOVSK", "УЛЬ": "ULYANOVSK",
    
    # LIPETSK
    "ЛИПЕЦК": "LIPETSK", "ЛИП": "LIPETSK", "ЛИПЕ": "LIPETSK",
    
    # BARNAUL
    "БАРНАУЛ": "BARNAUL", "БАРН": "BARNAUL", "БАР": "BARNAUL",
    
    # YAROSLAVL
    "ЯРОСЛАВЛЬ": "YAROSLAVL", "ЯРОС": "YAROSLAVL", "ЯР": "YAROSLAVL", "ЯРИК": "YAROSLAVL",
    
    # OREL
    "ОРЕЛ": "OREL", "ОРЁЛ": "OREL", "ОРЕ": "OREL",
    
    # BRYANSK
    "БРЯНСК": "BRYANSK", "БРЯ": "BRYANSK", "БРЯН": "BRYANSK",
    
    # PSKOV
    "ПСКОВ": "PSKOV", "ПСК": "PSKOV", "ПСКОВ": "PSKOV",
    
    # SMOLENSK
    "СМОЛЕНСК": "SMOLENSK", "СМОЛ": "SMOLENSK", "СМО": "SMOLENSK",
    
    # STAVROPOL
    "СТАВРОПОЛЬ": "STAVROPOL", "СТАВР": "STAVROPOL", "СТАВ": "STAVROPOL",
    
    # IVANOVO
    "ИВАНОВО": "IVANOVO", "ИВАН": "IVANOVO", "ИВАН": "IVANOVO",
    
    # TOLYATTI
    "ТОЛЬЯТТИ": "TOLYATTI", "ТОЛЬ": "TOLYATTI", "ТОЛ": "TOLYATTI", "ТОЛИК": "TOLYATTI",
    
    # TYUMEN
    "ТЮМЕНЬ": "TYUMEN", "ТЮМ": "TYUMEN", "ТЮМЯ": "TYUMEN",
    
    # KEMEROVO
    "КЕМЕРОВО": "KEMEROVO", "КЕМ": "KEMEROVO", "КЕМЕР": "KEMEROVO",
    
    # KIROV
    "КИРОВ": "KIROV", "КИР": "KIROV", "КИРА": "KIROV",
    
    # ORENBURG
    "ОРЕНБУРГ": "ORENBURG", "ОРЕН": "ORENBURG", "ОР": "ORENBURG", "ОРБ": "ORENBURG",
    
    # ARKHANGELSK
    "АРХАНГЕЛЬСК": "ARKHANGELSK", "АРХ": "ARKHANGELSK", "АРХАН": "ARKHANGELSK",
    
    # KURSK
    "КУРСК": "KURSK", "КУР": "KURSK", "КУРС": "KURSK",
    
    # MURMANSK
    "МУРМАНСК": "MURMANSK", "МУР": "MURMANSK", "МУРМАН": "MURMANSK",
    
    # PENZA
    "ПЕНЗА": "PENZA", "ПЕН": "PENZA", "ПЕНЗ": "PENZA",
    
    # RYAZAN
    "РЯЗАНЬ": "RYAZAN", "РЯЗ": "RYAZAN", "РЯЗА": "RYAZAN",
    
    # TULA
    "ТУЛА": "TULA", "ТУЛ": "TULA", "ТУЛЬ": "TULA",
    
    # PERM
    "ПЕРМЬ": "PERM", "ПЕР": "PERM", "ПЕРМ": "PERM",
    
    # KHABAROVSK
    "ХАБАРОВСК": "KHABAROVSK", "ХАБ": "KHABAROVSK", "ХАБАР": "KHABAROVSK",
    
    # CHEBOKSARY
    "ЧЕБОКСАРЫ": "CHEBOKSARY", "ЧЕБ": "CHEBOKSARY", "ЧЕБО": "CHEBOKSARY",
    
    # KRASNOYARSK
    "КРАСНОЯРСК": "KRASNOYARSK", "КРАСНОЯР": "KRASNOYARSK", "КРАС": "KRASNOYARSK", "КРС": "KRASNOYARSK",
    
    # CHELYABINSK
    "ЧЕЛЯБИНСК": "CHELYABINSK", "ЧЕЛ": "CHELYABINSK", "ЧЕЛЯ": "CHELYABINSK", "ЧЕЛЯБ": "CHELYABINSK",
    
    # KALININGRAD
    "КАЛИНИНГРАД": "KALININGRAD", "КАЛИ": "KALININGRAD", "КАЛ": "KALININGRAD", "КЁНИГ": "KALININGRAD",
    
    # VLADIVOSTOK
    "ВЛАДИВОСТОК": "VLADIVOSTOK", "ВЛАДИК": "VLADIVOSTOK", "ВЛАД": "VLADIVOSTOK", "ВЛ": "VLADIVOSTOK",
    
    # VLADIKAVKAZ
    "ВЛАДИКАВКАЗ": "VLADIKAVKAZ", "ВЛАДИК": "VLADIKAVKAZ", "ВЛАД": "VLADIKAVKAZ",
    
    # MAKHACHKALA
    "МАХАЧКАЛА": "MAKHACHKALA", "МАХА": "MAKHACHKALA", "МАХ": "MAKHACHKALA",
    
    # BELGOROD
    "БЕЛГОРОД": "BELGOROD", "БЕЛ": "BELGOROD", "БЕЛГО": "BELGOROD",
    
    # VORONEZH
    "ВОРОНЕЖ": "VORONEZH", "ВОРОН": "VORONEZH", "ВОР": "VORONEZH",
    
    # VOLGOGRAD
    "ВОЛГОГРАД": "VOLGOGRAD", "ВОЛГ": "VOLGOGRAD", "ВОЛГА": "VOLGOGRAD",
    
    # IRKUTSK
    "ИРКУТСК": "IRKUTSK", "ИРК": "IRKUTSK", "ИРКУТ": "IRKUTSK",
    
    # OMSK
    "ОМСК": "OMSK", "ОМ": "OMSK", "ОМС": "OMSK",
    
    # SARATOV
    "САРАТОВ": "SARATOV", "САР": "SARATOV", "САРА": "SARATOV",
    
    # GROZNY
    "ГРОЗНЫЙ": "GROZNY", "ГРОЗ": "GROZNY", "ГРОЗН": "GROZNY",
    
    # ARZAMAS
    "АРЗАМАС": "ARZAMAS", "АРЗ": "ARZAMAS", "АРЗА": "ARZAMAS",
    
    # ===== ПОПУЛЯРНЫЕ ГОРОДА =====
    "МОСКВА": "MOSCOW", "МСК": "MOSCOW", "МОС": "MOSCOW", "МОСК": "MOSCOW",
    
    "ПИТЕР": "SPB", "СПБ": "SPB", "САНКТ-ПЕТЕРБУРГ": "SPB", "ЛЕНИНГРАД": "SPB", 
    "ПЕТЕРБУРГ": "SPB", "ЛЕГ": "SPB",
    
    "КАЗАНЬ": "KAZAN", "КАЗАН": "KAZAN", "КАЗ": "KAZAN",
    
    "ЕКБ": "EKB", "ЕКАТЕРИНБУРГ": "EKB", "ЕКАТ": "EKB", "ЕКА": "EKB",
    
    "НОВОСИБ": "NOVOSIB", "НОВОСИБИРСК": "NOVOSIB", "НОВОС": "NOVOSIB",
    
    "КРАСНОДАР": "KRASNODAR", "КРД": "KRASNODAR", "КРАСНО": "KRASNODAR",
    
    "СОЧИ": "SOCHI", "СОЧ": "SOCHI", "СОЧИ": "SOCHI",
    
    "УФА": "UFA", "УФ": "UFA", "УФА": "UFA",
    
    "РОСТОВ": "ROSTOV", "РОСТОВ-НА-ДОНУ": "ROSTOV", "РНД": "ROSTOV", "РОСТ": "ROSTOV",
    
    "САМАРА": "SAMARA", "САМ": "SAMARA", "САМА": "SAMARA",
    
    "НИЖНИЙ НОВГОРОД": "NOVGOROD", "НН": "NOVGOROD", "НИЖНИЙ": "NOVGOROD",
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

# ========== ПРОВЕРКА ДОСТУПА ==========
async def check_private_access(update: Update):
    if update.message.chat.type != "private":
        return True
    if update.effective_user.id == OWNER_ID:
        return True
    await update.message.reply_text("⛔ Бот доступен только в группе")
    return False

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

# ========== УЛУЧШЕННАЯ ФУНКЦИЯ ОБНОВЛЕНИЯ СПИСКА ==========
async def update_list_message(context):
    """Обновляет закреплённое сообщение со списком"""
    full_text = format_list()
    current_message_id = load_message_id()
    
    try:
        # Сначала пробуем отредактировать по сохранённому ID
        if current_message_id:
            try:
                await context.bot.edit_message_text(
                    chat_id=CHAT_ID,
                    message_id=current_message_id,
                    text=full_text
                )
                # Если дошли сюда - значит успешно отредактировали
                return
            except Exception as e:
                error_str = str(e)
                # Если текст не изменился - просто игнорируем
                if "Message is not modified" in error_str:
                    return
                # Если сообщение не найдено или нельзя редактировать - продолжаем
                elif "Message can't be edited" in error_str or "message to edit not found" in error_str.lower():
                    pass
                else:
                    logging.warning(f"⚠️ {error_str}")
        
        # Пробуем найти закреплённое сообщение в чате
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
                # Игнорируем остальные ошибки
        
        # Если ничего не помогло - создаём новое сообщение
        sent_message = await context.bot.send_message(chat_id=CHAT_ID, text=full_text)
        
        # Пробуем закрепить
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

# ========== КОМАНДА START ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_private_access(update):
        return
    
    await update.message.reply_text(
        "чтобы записать слет /i (сервер/\n"
        "пример /i блу бусс 22 или /i москва кор 20"
    )
    await update_list_message(context)

# ========== КОМАНДА ДОБАВЛЕНИЯ ==========
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
    
    await update.message.reply_text(f"✅ Записано на {server}: {text}")
    await update_list_message(context)

# ========== КОМАНДА СПИСОК ==========
async def list_entries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_private_access(update):
        return
    
    full_list = format_list()
    if len(full_list) > 4096:
        for i in range(0, len(full_list), 4096):
            await update.message.reply_text(full_list[i:i+4096])
    else:
        await update.message.reply_text(full_list)

# ========== КОМАНДА ОЧИСТКИ ==========
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

# ========== КОМАНДА ЛОГИ ==========
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

# ========== КОМАНДА ОЧИСТКИ ЛОГОВ ==========
async def clear_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Только для владельца")
        return
    
    save_logs([])
    await update.message.reply_text("🗑 Логи очищены")

# ========== КОМАНДА НОВОГО СПИСКА ==========
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
    await update.message.reply_text("✅ Новый список готов!")

# ========== АВТОМАТИЧЕСКИЙ ПЕРЕЗАПУСК ==========
async def auto_start(context: ContextTypes.DEFAULT_TYPE):
    class FakeMessage:
        def __init__(self):
            self.chat_id = CHAT_ID
            self.chat = type('obj', (object,), {'type': 'group'})
        async def reply_text(self, text):
            await context.bot.send_message(chat_id=CHAT_ID, text=text)
    
    class FakeUpdate:
        def __init__(self):
            self.message = FakeMessage()
            self.effective_user = type('obj', (object,), {'id': OWNER_ID})
    
    await start(FakeUpdate(), context)

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
        logging.info("✅ Автоматический перезапуск запланирован")
    
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


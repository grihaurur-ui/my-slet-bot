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

# ========== ПОЛНЫЕ СИНОНИМЫ ДЛЯ ВСЕХ СЕРВЕРОВ И ЦВЕТОВ ==========
SYNONYMS = {
    # ===== ЦВЕТА =====
    # WHITE - белый
    "ВАЙТ": "WHITE", "БЕЛЫЙ": "WHITE", "ВЙТ": "WHITE", "УАЙТ": "WHITE", 
    "БЕЛ": "WHITE", "БЕЛА": "WHITE", "БЕЛО": "WHITE", "БЕЛЕН": "WHITE",
    "УАЙТ": "WHITE", "УАЙТИ": "WHITE", "БЕЛОСНЕЖНЫЙ": "WHITE",
    
    # BLUE - синий
    "БЛУ": "BLUE", "СИНИЙ": "BLUE", "БЛЮ": "BLUE", "БЛУУ": "BLUE", 
    "СИН": "BLUE", "СИНЬ": "BLUE", "СИНЯ": "BLUE", "БЛ": "BLUE",
    "СИНИЙ": "BLUE", "СИНИЙ": "BLUE", "ЛАЗУРНЫЙ": "BLUE", "ГОЛУБОЙ": "BLUE",
    
    # GREEN - зеленый
    "ГРИН": "GREEN", "ЗЕЛЕНЫЙ": "GREEN", "ГРИНН": "GREEN", "ЗЕЛ": "GREEN", 
    "ЗЕЛЕН": "GREEN", "ЗЕЛЕНЬ": "GREEN", "ЗЕЛЕНА": "GREEN", "ГРН": "GREEN",
    "ЗЕЛЕНЫЙ": "GREEN", "ЗЕЛЕНЫЙ": "GREEN", "ИЗУМРУД": "GREEN", "САЛАТОВЫЙ": "GREEN",
    
    # GOLD - золото
    "ГОЛД": "GOLD", "ЗОЛОТО": "GOLD", "ГОЛДД": "GOLD", "ЗОЛ": "GOLD", 
    "ЗОЛОТ": "GOLD", "ЗОЛОТА": "GOLD", "ЗЛТ": "GOLD", "ГОЛ": "GOLD",
    "ЗОЛОТОЙ": "GOLD", "ЗОЛОТИСТЫЙ": "GOLD", "ГОЛДЕН": "GOLD",
    
    # PINK - розовый
    "ПИНК": "PINK", "РОЗОВЫЙ": "PINK", "ПИНКК": "PINK", "РОЗ": "PINK", 
    "РОЗОВ": "PINK", "РОЗОВА": "PINK", "РОЗА": "PINK", "ПНК": "PINK",
    "РОЗОВЫЙ": "PINK", "РОЗОВЕН": "PINK", "РОЗА": "PINK", "ФУКСИЯ": "PINK",
    
    # BLACK - черный
    "БЛЕК": "BLACK", "ЧЕРНЫЙ": "BLACK", "ЧЁРНЫЙ": "BLACK", "БЛЕКК": "BLACK", 
    "ЧЕРН": "BLACK", "ЧЕРНА": "BLACK", "ЧОРНЫЙ": "BLACK", "БЛК": "BLACK",
    "ЧЕРНЫЙ": "BLACK", "ЧЕРНЕН": "BLACK", "ЧЕРНОТА": "BLACK", "УГОЛЬ": "BLACK",
    
    # RED - красный
    "РЭД": "RED", "РЕД": "RED", "КРАСНЫЙ": "RED", "РЭДД": "RED", 
    "КРАСН": "RED", "КРАС": "RED", "КРАСНА": "RED", "КРСН": "RED",
    "КРАСНЫЙ": "RED", "АЛЫЙ": "RED", "РУБИН": "RED", "БАГРОВЫЙ": "RED",
    
    # ORANGE - оранжевый
    "ОРАНЖ": "ORANGE", "ОРАНЖЕВЫЙ": "ORANGE", "ОРАНЖЖ": "ORANGE", "ОРАН": "ORANGE", 
    "АПЕЛЬСИН": "ORANGE", "ОРЕНЖ": "ORANGE", "ОРЕНДЖ": "ORANGE", "ОРАНДЖ": "ORANGE",
    "ОРАНГ": "ORANGE", "ОРНЖ": "ORANGE", "ОРА": "ORANGE", "ОРАНЖИК": "ORANGE",
    
    # PURPLE - фиолетовый
    "ПЁРПЛ": "PURPLE", "ПУРПЛ": "PURPLE", "ФИОЛЕТОВЫЙ": "PURPLE", "ПУРПУР": "PURPLE", 
    "ФИОЛ": "PURPLE", "ФИОЛЕТ": "PURPLE", "ЛИЛОВЫЙ": "PURPLE", "ПРПЛ": "PURPLE",
    "ФИОЛКА": "PURPLE", "ФИОЛЯ": "PURPLE", "СИРЕНЕВЫЙ": "PURPLE",
    
    # LIME - лайм
    "ЛАЙМ": "LIME", "ЛАЙММ": "LIME", "ЛАЙМОВЫЙ": "LIME", "ЛАЙМА": "LIME",
    "ЛАЙМ": "LIME", "ЛАЙМЧИК": "LIME", "ЛАЙМУС": "LIME", "САЛАТОВЫЙ": "LIME",
    
    # CHERRY - вишня
    "ЧЕРРИ": "CHERRY", "ВИШНЯ": "CHERRY", "ЧЕРИ": "CHERRY", "ВИШ": "CHERRY", 
    "ВИШН": "CHERRY", "ВИШНЕВЫЙ": "CHERRY", "ЧЕР": "CHERRY", "ВИШНЯК": "CHERRY",
    
    # INDIGO - индиго
    "ИНДИГО": "INDIGO", "ИНД": "INDIGO", "ИНДИГА": "INDIGO", "ИНДИК": "INDIGO",
    "ИНДИГО": "INDIGO", "ИНДИГОВЫЙ": "INDIGO", "СИНЕ-ФИОЛЕТОВЫЙ": "INDIGO",
    
    # MAGENTA - маджента
    "МАДЖЕНТА": "MAGENTA", "МАДЖЕНТТА": "MAGENTA", "МАДЖ": "MAGENTA", "МАДЖА": "MAGENTA",
    "МАДЖЕН": "MAGENTA", "МАГЕНТА": "MAGENTA", "МДЖН": "MAGENTA", "ПУРПУРНЫЙ": "MAGENTA",
    
    # CRIMSON - малиновый
    "КРИМСОН": "CRIMSON", "КРИМЗОН": "CRIMSON", "КРИМ": "CRIMSON", "МАЛИНОВЫЙ": "CRIMSON",
    "КРИМС": "CRIMSON", "КРИМСОН": "CRIMSON", "КРМСН": "CRIMSON", "БАГРОВЫЙ": "CRIMSON",
    
    # AQUA - аква
    "АКВА": "AQUA", "АКВВА": "AQUA", "АКВ": "AQUA", "МОРСКОЙ": "AQUA",
    "АКВАМАРИН": "AQUA", "АКВА": "AQUA", "АКВ": "AQUA", "БИРЮЗОВЫЙ": "AQUA",
    
    # GRAY - серый
    "ГРЕЙ": "GRAY", "СЕРЫЙ": "GRAY", "ГРЭЙ": "GRAY", "СЕР": "GRAY",
    "СЕРА": "GRAY", "СЕРО": "GRAY", "ГРЕЙ": "GRAY", "ГРЙ": "GRAY",
    "СЕРЕБРО": "GRAY", "СЕРЕБРИСТЫЙ": "GRAY",
    
    # LCE - лёд/айс
    "ЛЦЕ": "LCE", "ЛСЕ": "LCE", "АЙС": "LCE", "ICE": "LCE", 
    "ЛЁД": "LCE", "ЛЕД": "LCE", "ЛЕДЯНОЙ": "LCE", "ЛЕДО": "LCE",
    "ЛЬДИНКА": "LCE", "ЛЕДНИК": "LCE", "ХОЛОДНЫЙ": "LCE", "ФРОСТ": "LCE",
    
    # CHILLI - чили
    "ЧИЛЛИ": "CHILLI", "ЧИЛИ": "CHILLI", "ЧИЛ": "CHILLI", "ПЕРЕЦ": "CHILLI",
    "ЧИЛИЙ": "CHILLI", "ЧИЛЬ": "CHILLI", "ЧЛ": "CHILLI", "ОСТРЫЙ": "CHILLI",
    
    # COCO - коко
    "КОКО": "COCO", "КОКОС": "COCO", "ЧОКО": "COCO", "CHOCO": "COCO", 
    "ШОКО": "COCO", "КОКОСОВЫЙ": "COCO", "КОКОСИК": "COCO", "КОКОС": "COCO",
    
    # PLATINUM - платина
    "ПЛАТИНУМ": "PLATINUM", "ПЛАТИНА": "PLATINUM", "ПЛАТ": "PLATINUM",
    "ПЛАТИН": "PLATINUM", "ПЛТН": "PLATINUM", "ПЛАТИНОВЫЙ": "PLATINUM",
    
    # AQURE - азур
    "АКУРЕ": "AQURE", "АКУРЭ": "AQURE", "АКУР": "AQURE", "АЗУР": "AQURE", 
    "AZUR": "AQURE", "АЗУРНЫЙ": "AQURE", "АЗУР": "AQURE", "АКУР": "AQURE",

    # ===== NORILSK =====
    "НОРИЛЬСК": "NORILSK", "НОРИЛ": "NORILSK", "НОР": "NORILSK", "НРК": "NORILSK", 
    "НОРИК": "NORILSK", "НОРЯ": "NORILSK", "НОРА": "NORILSK", "НОРИЛЬ": "NORILSK",
    
    # ===== CHEREPOVETS =====
    "ЧЕРЕПОВЕЦ": "CHEREPOVETS", "ЧЕРЕП": "CHEREPOVETS", "ЧЕРЕПА": "CHEREPOVETS", 
    "ЧЕР": "CHEREPOVETS", "ЧРП": "CHEREPOVETS", "ЧЕРЕПОВЕЦК": "CHEREPOVETS",
    "ЧЕРЕПОК": "CHEREPOVETS", "ЧЕРА": "CHEREPOVETS", "ЧРПВ": "CHEREPOVETS",
    
    # ===== MAGADAN =====
    "МАГАДАН": "MAGADAN", "МАГА": "MAGADAN", "МАГ": "MAGADAN", "МГД": "MAGADAN",
    "МАГАД": "MAGADAN", "МАГД": "MAGADAN", "МАГАН": "MAGADAN", "МАГАДАНЧИК": "MAGADAN",
    
    # ===== PODOLSK =====
    "ПОДОЛЬСК": "PODOLSK", "ПОДОЛ": "PODOLSK", "ПОД": "PODOLSK", "ПДЛ": "PODOLSK",
    "ПОДО": "PODOLSK", "ПОДЬ": "PODOLSK", "ПОДЛ": "PODOLSK", "ПОДОЛЬ": "PODOLSK",
    
    # ===== SURGUT =====
    "СУРГУТ": "SURGUT", "СУР": "SURGUT", "СУРГ": "SURGUT", "СРГ": "SURGUT",
    "СУРГА": "SURGUT", "СУРУ": "SURGUT", "СУГ": "SURGUT", "СУРГУТИК": "SURGUT",
    
    # ===== IZHEVSK =====
    "ИЖЕВСК": "IZHEVSK", "ИЖ": "IZHEVSK", "ИЖЕВ": "IZHEVSK", "ИЖВ": "IZHEVSK",
    "ИЖА": "IZHEVSK", "ИЖЕ": "IZHEVSK", "ИЖОВ": "IZHEVSK", "ИЖЕВСКИЙ": "IZHEVSK",
    
    # ===== TOMSK =====
    "ТОМСК": "TOMSK", "ТОМ": "TOMSK", "ТОМС": "TOMSK", "ТМС": "TOMSK",
    "ТОМА": "TOMSK", "ТОМИ": "TOMSK", "ТОМК": "TOMSK", "ТОМИЧИ": "TOMSK",
    
    # ===== TVER =====
    "ТВЕРЬ": "TVER", "ТВЕР": "TVER", "ТВЬ": "TVER", "ТВР": "TVER",
    "ТВЕРА": "TVER", "ТВЕРЯ": "TVER", "ТВРЬ": "TVER", "ТВЕРИЧИ": "TVER",
    
    # ===== VOLOGDA =====
    "ВОЛОГДА": "VOLOGDA", "ВОЛО": "VOLOGDA", "ВОЛ": "VOLOGDA", "ВЛГ": "VOLOGDA",
    "ВОЛОГ": "VOLOGDA", "ВОЛГА": "VOLOGDA", "ВОЛДА": "VOLOGDA", "ВОЛОГЖАНЕ": "VOLOGDA",
    
    # ===== TAGANROG =====
    "ТАГАНРОГ": "TAGANROG", "ТАГАН": "TAGANROG", "ТАГ": "TAGANROG", "ТГН": "TAGANROG",
    "ТАГА": "TAGANROG", "ТАГРОГ": "TAGANROG", "ТГР": "TAGANROG", "ТАГАНРОЖАНЕ": "TAGANROG",
    
    # ===== NOVGOROD =====
    "НОВГОРОД": "NOVGOROD", "НОВГОР": "NOVGOROD", "НОВ": "NOVGOROD", "НВГ": "NOVGOROD",
    "ВЕЛИКИЙ НОВГОРОД": "NOVGOROD", "НИЖНИЙ НОВГОРОД": "NOVGOROD", "НН": "NOVGOROD",
    "НИЖНИЙ": "NOVGOROD", "НЖН": "NOVGOROD", "НОВГ": "NOVGOROD", "НОВОР": "NOVGOROD",
    
    # ===== KALUGA =====
    "КАЛУГА": "KALUGA", "КАЛ": "KALUGA", "КАЛУ": "KALUGA", "КЛГ": "KALUGA",
    "КАЛУГ": "KALUGA", "КАЛГА": "KALUGA", "КЛУ": "KALUGA", "КАЛУЖАНЕ": "KALUGA",
    
    # ===== VLADIMIR =====
    "ВЛАДИМИР": "VLADIMIR", "ВЛАД": "VLADIMIR", "ВЛАДИ": "VLADIMIR", "ВЛД": "VLADIMIR",
    "ВЛАДИК": "VLADIMIR", "ВЛАДИМ": "VLADIMIR", "ВЛАДЯ": "VLADIMIR", "ВЛАДИМИРЧИК": "VLADIMIR",
    
    # ===== KOSTROMA =====
    "КОСТРОМА": "KOSTROMA", "КОСТР": "KOSTROMA", "КОСТЯ": "KOSTROMA", "КОС": "KOSTROMA", 
    "КСТ": "KOSTROMA", "КОСТ": "KOSTROMA", "КОСТРО": "KOSTROMA", "КОСТРОМИЧИ": "KOSTROMA",
    
    # ===== CHITA =====
    "ЧИТА": "CHITA", "ЧИТ": "CHITA", "ЧТА": "CHITA", "ЧИТА": "CHITA",
    "ЧИТК": "CHITA", "ЧИТО": "CHITA", "ЧИ": "CHITA", "ЧИТИНЦЫ": "CHITA",
    
    # ===== ASTRAKHAN =====
    "АСТРАХАНЬ": "ASTRAKHAN", "АСТРА": "ASTRAKHAN", "АСТ": "ASTRAKHAN", "АСТР": "ASTRAKHAN", 
    "АСТХ": "ASTRAKHAN", "АСТРАХ": "ASTRAKHAN", "АСТРАХА": "ASTRAKHAN", "АСТХН": "ASTRAKHAN",
    
    # ===== BRATSK =====
    "БРАТСК": "BRATSK", "БРАТ": "BRATSK", "БРАТС": "BRATSK", "БРТ": "BRATSK",
    "БРАТА": "BRATSK", "БРАТК": "BRATSK", "БРАЦК": "BRATSK", "БРАТЧАНЕ": "BRATSK",
    
    # ===== TAMBOV =====
    "ТАМБОВ": "TAMBOV", "ТАМ": "TAMBOV", "ТАМБ": "TAMBOV", "ТМБ": "TAMBOV",
    "ТАМБА": "TAMBOV", "ТАМОВ": "TAMBOV", "ТАБ": "TAMBOV", "ТАМБОВЧАНЕ": "TAMBOV",
    
    # ===== YAKUTSK =====
    "ЯКУТСК": "YAKUTSK", "ЯКУТ": "YAKUTSK", "ЯК": "YAKUTSK", "ЯКТ": "YAKUTSK",
    "ЯКУТА": "YAKUTSK", "ЯКУЦК": "YAKUTSK", "ЯКУ": "YAKUTSK", "ЯКУТЯНЕ": "YAKUTSK",
    
    # ===== ULYANOVSK =====
    "УЛЬЯНОВСК": "ULYANOVSK", "УЛЬЯ": "ULYANOVSK", "УЛЬ": "ULYANOVSK", "УЛБ": "ULYANOVSK",
    "УЛЬЯН": "ULYANOVSK", "УЛЬЯНО": "ULYANOVSK", "УЛН": "ULYANOVSK", "УЛЬЯНОВЧАНЕ": "ULYANOVSK",
    
    # ===== LIPETSK =====
    "ЛИПЕЦК": "LIPETSK", "ЛИП": "LIPETSK", "ЛИПЕ": "LIPETSK", "ЛПЦ": "LIPETSK",
    "ЛИПА": "LIPETSK", "ЛИПЕК": "LIPETSK", "ЛИПЦ": "LIPETSK", "ЛИПЧАНЕ": "LIPETSK",
    
    # ===== BARNAUL =====
    "БАРНАУЛ": "BARNAUL", "БАРН": "BARNAUL", "БАР": "BARNAUL", "БРН": "BARNAUL",
    "БАРНА": "BARNAUL", "БАРНУЛ": "BARNAUL", "БАРНЛ": "BARNAUL", "БАРНАУЛЬЦЫ": "BARNAUL",
    
    # ===== YAROSLAVL =====
    "ЯРОСЛАВЛЬ": "YAROSLAVL", "ЯРОС": "YAROSLAVL", "ЯР": "YAROSLAVL", "ЯРИК": "YAROSLAVL", 
    "ЯРС": "YAROSLAVL", "ЯРОСЛ": "YAROSLAVL", "ЯРОСЛАВ": "YAROSLAVL", "ЯРЛ": "YAROSLAVL",
    
    # ===== OREL =====
    "ОРЕЛ": "OREL", "ОРЁЛ": "OREL", "ОРЕ": "OREL", "ОРЛ": "OREL",
    "ОРИК": "OREL", "ОРЛАН": "OREL", "ОРЕЛ": "OREL", "ОРЛОВЧАНЕ": "OREL",
    
    # ===== BRYANSK =====
    "БРЯНСК": "BRYANSK", "БРЯ": "BRYANSK", "БРЯН": "BRYANSK", "БРН": "BRYANSK", "БРС": "BRYANSK",
    "БРЯНА": "BRYANSK", "БРЯНК": "BRYANSK", "БРЯС": "BRYANSK", "БРЯНЧАНЕ": "BRYANSK",
    
    # ===== PSKOV =====
    "ПСКОВ": "PSKOV", "ПСК": "PSKOV", "ПСКВ": "PSKOV", "ПСКО": "PSKOV",
    "ПСКОВА": "PSKOV", "ПСКОВЬ": "PSKOV", "ПСКО": "PSKOV", "ПСКОВИЧИ": "PSKOV",
    
    # ===== SMOLENSK =====
    "СМОЛЕНСК": "SMOLENSK", "СМОЛ": "SMOLENSK", "СМО": "SMOLENSK", "СМЛ": "SMOLENSK",
    "СМОЛЕН": "SMOLENSK", "СМОЛЯ": "SMOLENSK", "СМЛН": "SMOLENSK", "СМОЛЯНЕ": "SMOLENSK",
    
    # ===== STAVROPOL =====
    "СТАВРОПОЛЬ": "STAVROPOL", "СТАВР": "STAVROPOL", "СТАВ": "STAVROPOL", "СТВ": "STAVROPOL",
    "СТАВРО": "STAVROPOL", "СТАВРОП": "STAVROPOL", "СТАВРП": "STAVROPOL", "СТАВРОПОЛЬЦЫ": "STAVROPOL",
    
    # ===== IVANOVO =====
    "ИВАНОВО": "IVANOVO", "ИВАН": "IVANOVO", "ИВН": "IVANOVO", "ИВАНО": "IVANOVO",
    "ИВАНЫЧ": "IVANOVO", "ИВАНЬ": "IVANOVO", "ИВНВ": "IVANOVO", "ИВАНОВЦЫ": "IVANOVO",
    
    # ===== TOLYATTI =====
    "ТОЛЬЯТТИ": "TOLYATTI", "ТОЛЬ": "TOLYATTI", "ТОЛ": "TOLYATTI", "ТОЛИК": "TOLYATTI", 
    "ТЛТ": "TOLYATTI", "ТОЛЬЯ": "TOLYATTI", "ТОЛЯ": "TOLYATTI", "ТЛЯ": "TOLYATTI",
    
    # ===== TYUMEN =====
    "ТЮМЕНЬ": "TYUMEN", "ТЮМ": "TYUMEN", "ТЮМЯ": "TYUMEN", "ТМН": "TYUMEN",
    "ТЮМЕН": "TYUMEN", "ТЮМА": "TYUMEN", "ТЮМН": "TYUMEN", "ТЮМЕНЦЫ": "TYUMEN",
    
    # ===== KEMEROVO =====
    "КЕМЕРОВО": "KEMEROVO", "КЕМ": "KEMEROVO", "КЕМЕР": "KEMEROVO", "КМР": "KEMEROVO",
    "КЕМЕРО": "KEMEROVO", "КЕМРОВ": "KEMEROVO", "КЕМЕР": "KEMEROVO", "КЕМЕРОВЧАНЕ": "KEMEROVO",
    
    # ===== KIROV =====
    "КИРОВ": "KIROV", "КИР": "KIROV", "КИРА": "KIROV", "КРВ": "KIROV",
    "КИРОВА": "KIROV", "КИРОВЕ": "KIROV", "КИРВ": "KIROV", "КИРОВЧАНЕ": "KIROV",
    
    # ===== ORENBURG =====
    "ОРЕНБУРГ": "ORENBURG", "ОРЕН": "ORENBURG", "ОР": "ORENBURG", "ОРБ": "ORENBURG", 
    "ОРН": "ORENBURG", "ОРЕНБ": "ORENBURG", "ОРЕНУРГ": "ORENBURG", "ОРНБ": "ORENBURG",
    
    # ===== ARKHANGELSK =====
    "АРХАНГЕЛЬСК": "ARKHANGELSK", "АРХ": "ARKHANGELSK", "АРХАН": "ARKHANGELSK", 
    "АРХГ": "ARKHANGELSK", "АРХАНГ": "ARKHANGELSK", "АРХА": "ARKHANGELSK", "АРХНГ": "ARKHANGELSK",
    
    # ===== KURSK =====
    "КУРСК": "KURSK", "КУР": "KURSK", "КУРС": "KURSK", "КРС": "KURSK",
    "КУРА": "KURSK", "КУРСКА": "KURSK", "КУРСЬ": "KURSK", "КУРЯНЕ": "KURSK",
    
    # ===== MURMANSK =====
    "МУРМАНСК": "MURMANSK", "МУР": "MURMANSK", "МУРМАН": "MURMANSK", "МРМ": "MURMANSK",
    "МУРМА": "MURMANSK", "МУРМАНЬ": "MURMANSK", "МУРМН": "MURMANSK", "МУРМАНЧАНЕ": "MURMANSK",
    
    # ===== PENZA =====
    "ПЕНЗА": "PENZA", "ПЕН": "PENZA", "ПЕНЗ": "PENZA", "ПНЗ": "PENZA",
    "ПЕНЗАК": "PENZA", "ПЕНЗЯ": "PENZA", "ПЕНЗЬ": "PENZA", "ПЕНЗЕНЦЫ": "PENZA",
    
    # ===== RYAZAN =====
    "РЯЗАНЬ": "RYAZAN", "РЯЗ": "RYAZAN", "РЯЗА": "RYAZAN", "РЗН": "RYAZAN",
    "РЯЗАН": "RYAZAN", "РЯЗЬ": "RYAZAN", "РЯЗН": "RYAZAN", "РЯЗАНЦЫ": "RYAZAN",
    
    # ===== TULA =====
    "ТУЛА": "TULA", "ТУЛ": "TULA", "ТУЛЬ": "TULA", "ТЛ": "TULA",
    "ТУЛЯ": "TULA", "ТУЛИК": "TULA", "ТУЛЬЯ": "TULA", "ТУЛЯКИ": "TULA",
    
    # ===== PERM =====
    "ПЕРМЬ": "PERM", "ПЕР": "PERM", "ПЕРМ": "PERM", "ПРМ": "PERM",
    "ПЕРМА": "PERM", "ПЕРМЯ": "PERM", "ПЕРМК": "PERM", "ПЕРМЯКИ": "PERM",
    
    # ===== KHABAROVSK =====
    "ХАБАРОВСК": "KHABAROVSK", "ХАБ": "KHABAROVSK", "ХАБАР": "KHABAROVSK", "ХБР": "KHABAROVSK",
    "ХАБАРОВ": "KHABAROVSK", "ХАБАРКА": "KHABAROVSK", "ХАБР": "KHABAROVSK", "ХАБАРОВЧАНЕ": "KHABAROVSK",
    
    # ===== CHEBOKSARY =====
    "ЧЕБОКСАРЫ": "CHEBOKSARY", "ЧЕБ": "CHEBOKSARY", "ЧЕБО": "CHEBOKSARY", "ЧБК": "CHEBOKSARY",
    "ЧЕБОК": "CHEBOKSARY", "ЧЕБОКСАР": "CHEBOKSARY", "ЧЕБК": "CHEBOKSARY", "ЧЕБОКСАРЦЫ": "CHEBOKSARY",
    
    # ===== KRASNOYARSK =====
    "КРАСНОЯРСК": "KRASNOYARSK", "КРАСНОЯР": "KRASNOYARSK", "КРАС": "KRASNOYARSK", 
    "КРС": "KRASNOYARSK", "КРСК": "KRASNOYARSK", "КРАСЯР": "KRASNOYARSK", "КРАЯР": "KRASNOYARSK",
    
    # ===== CHELYABINSK =====
    "ЧЕЛЯБИНСК": "CHELYABINSK", "ЧЕЛ": "CHELYABINSK", "ЧЕЛЯ": "CHELYABINSK", 
    "ЧЕЛЯБ": "CHELYABINSK", "ЧЛБ": "CHELYABINSK", "ЧЕЛЯБА": "CHELYABINSK", "ЧЕЛБ": "CHELYABINSK",
    
    # ===== KALININGRAD =====
    "КАЛИНИНГРАД": "KALININGRAD", "КАЛИ": "KALININGRAD", "КАЛ": "KALININGRAD", 
    "КЁНИГ": "KALININGRAD", "КЛН": "KALININGRAD", "КАЛИК": "KALININGRAD", "КАЛИН": "KALININGRAD",
    
    # ===== VLADIVOSTOK =====
    "ВЛАДИВОСТОК": "VLADIVOSTOK", "ВЛАДИК": "VLADIVOSTOK", "ВЛАД": "VLADIVOSTOK", 
    "ВЛ": "VLADIVOSTOK", "ВЛД": "VLADIVOSTOK", "ВЛАДИВО": "VLADIVOSTOK", "ВЛАДВ": "VLADIVOSTOK",
    
    # ===== VLADIKAVKAZ =====
    "ВЛАДИКАВКАЗ": "VLADIKAVKAZ", "ВЛАДИК": "VLADIKAVKAZ", "ВЛАД": "VLADIKAVKAZ", 
    "ВЛК": "VLADIKAVKAZ", "ВЛАДИКА": "VLADIKAVKAZ", "ВЛАДК": "VLADIKAVKAZ",
    
    # ===== MAKHACHKALA =====
    "МАХАЧКАЛА": "MAKHACHKALA", "МАХА": "MAKHACHKALA", "МАХ": "MAKHACHKALA", 
    "МХЧ": "MAKHACHKALA", "МАХАЧ": "MAKHACHKALA", "МАХАК": "MAKHACHKALA", "МАХЧ": "MAKHACHKALA",
    
    # ===== BELGOROD =====
    "БЕЛГОРОД": "BELGOROD", "БЕЛ": "BELGOROD", "БЕЛГО": "BELGOROD", "БЛГ": "BELGOROD",
    "БЕЛГА": "BELGOROD", "БЕЛГОР": "BELGOROD", "БЕЛГР": "BELGOROD", "БЕЛГОРОДЧАНЕ": "BELGOROD",
    
    # ===== VORONEZH =====
    "ВОРОНЕЖ": "VORONEZH", "ВОРОН": "VORONEZH", "ВОР": "VORONEZH", "ВРН": "VORONEZH",
    "ВОРОНА": "VORONEZH", "ВОРОНЕ": "VORONEZH", "ВРОН": "VORONEZH", "ВОРОНЕЖЦЫ": "VORONEZH",
    
    # ===== VOLGOGRAD =====
    "ВОЛГОГРАД": "VOLGOGRAD", "ВОЛГ": "VOLGOGRAD", "ВОЛГА": "VOLGOGRAD", "ВЛГ": "VOLGOGRAD",
    "ВОЛГО": "VOLGOGRAD", "ВОЛГОГР": "VOLGOGRAD", "ВОЛГД": "VOLGOGRAD", "ВОЛГОГРАДЦЫ": "VOLGOGRAD",
    
    # ===== IRKUTSK =====
    "ИРКУТСК": "IRKUTSK", "ИРК": "IRKUTSK", "ИРКУТ": "IRKUTSK", "ИРК": "IRKUTSK", 
    "ИРТ": "IRKUTSK", "ИРКУЦК": "IRKUTSK", "ИРКУ": "IRKUTSK", "ИРКУТЯНЕ": "IRKUTSK",
    
    # ===== OMSK =====
    "ОМСК": "OMSK", "ОМ": "OMSK", "ОМС": "OMSK", "ОМК": "OMSK",
    "ОМА": "OMSK", "ОМСКИЙ": "OMSK", "ОМЬ": "OMSK", "ОМИЧИ": "OMSK",
    
    # ===== SARATOV =====
    "САРАТОВ": "SARATOV", "САР": "SARATOV", "САРА": "SARATOV", "СРТ": "SARATOV",
    "САРАТ": "SARATOV", "САРАТО": "SARATOV", "САРВ": "SARATOV", "САРАТОВЦЫ": "SARATOV",
    
    # ===== GROZNY =====
    "ГРОЗНЫЙ": "GROZNY", "ГРОЗ": "GROZNY", "ГРОЗН": "GROZNY", "ГРЗ": "GROZNY",
    "ГРОЗА": "GROZNY", "ГРОЗНО": "GROZNY", "ГРОЗЬ": "GROZNY", "ГРОЗНЕНЦЫ": "GROZNY",
    
    # ===== ARZAMAS =====
    "АРЗАМАС": "ARZAMAS", "АРЗ": "ARZAMAS", "АРЗА": "ARZAMAS", "АРЗМ": "ARZAMAS",
    "АРЗАМ": "ARZAMAS", "АРЗАС": "ARZAMAS", "АРЗМС": "ARZAMAS", "АРЗАМАСЦЫ": "ARZAMAS",
    
    # ===== ANAPA =====
    "АНАПА": "ANAPA", "АНП": "ANAPA", "АНА": "ANAPA", "АНАП": "ANAPA",
    "АНАПКА": "ANAPA", "АНАПА": "ANAPA", "АНПА": "ANAPA", "АНАПЧАНЕ": "ANAPA",

    # ===== POPULAR CITIES =====
    "МОСКВА": "MOSCOW", "МСК": "MOSCOW", "МОС": "MOSCOW", "МО": "MOSCOW",
    "МОСК": "MOSCOW", "МОСКОВ": "MOSCOW", "МСКВ": "MOSCOW", "МОСКВИЧИ": "MOSCOW",
    
    "ПИТЕР": "SPB", "СПБ": "SPB", "САНКТ-ПЕТЕРБУРГ": "SPB", "ЛЕНИНГРАД": "SPB", 
    "ПЕТЕРБУРГ": "SPB", "ЛЕГ": "SPB", "СП": "SPB", "ПИТ": "SPB", "СПБУРГ": "SPB",
    "ПИТЕРЦЫ": "SPB",
    
    "КАЗАНЬ": "KAZAN", "КАЗАН": "KAZAN", "КАЗ": "KAZAN", "КЗН": "KAZAN",
    "КАЗА": "KAZAN", "КАЗАНЬ": "KAZAN", "КЗН": "KAZAN", "КАЗАНЦЫ": "KAZAN",
    
    "ЕКБ": "EKB", "ЕКАТЕРИНБУРГ": "EKB", "ЕКАТ": "EKB", "ЕКА": "EKB", 
    "ЕК": "EKB", "ЕКАТЕР": "EKB", "ЕКАТЕРИН": "EKB", "ЕКБЦЫ": "EKB",
    
    "НОВОСИБ": "NOVOSIB", "НОВОСИБИРСК": "NOVOSIB", "НОВОС": "NOVOSIB", 
    "НСК": "NOVOSIB", "НОВ": "NOVOSIB", "НОВОСИБЬ": "NOVOSIB", "НОВСИБ": "NOVOSIB",
    "НОВОСИБИРЦЫ": "NOVOSIB",
    
    "КРАСНОДАР": "KRASNODAR", "КРД": "KRASNODAR", "КРАСНО": "KRASNODAR", 
    "КР": "KRASNODAR", "КРАС": "KRASNODAR", "КРАСНОД": "KRASNODAR", "КРНД": "KRASNODAR",
    "КРАСНОДАРЦЫ": "KRASNODAR",
    
    "СОЧИ": "SOCHI", "СОЧ": "SOCHI", "СЧ": "SOCHI", "СОЧА": "SOCHI",
    "СОЧИНСК": "SOCHI", "СОЧЬ": "SOCHI", "СОЧИ": "SOCHI", "СОЧИНЦЫ": "SOCHI",
    
    "УФА": "UFA", "УФ": "UFA", "УФА": "UFA", "УФИК": "UFA",
    "УФА": "UFA", "УФА": "UFA", "УФА": "UFA", "УФИМЦЫ": "UFA",
    
    "РОСТОВ": "ROSTOV", "РОСТОВ-НА-ДОНУ": "ROSTOV", "РНД": "ROSTOV", 
    "РОСТ": "ROSTOV", "РСТ": "ROSTOV", "РОСТОВ": "ROSTOV", "РСВ": "ROSTOV",
    "РОСТОВЧАНЕ": "ROSTOV",
    
    "САМАРА": "SAMARA", "САМ": "SAMARA", "САМА": "SAMARA", "СМР": "SAMARA",
    "САМАР": "SAMARA", "САМРА": "SAMARA", "СМРА": "SAMARA", "САМАРЦЫ": "SAMARA",
    
    "НИЖНИЙ НОВГОРОД": "NOVGOROD", "НН": "NOVGOROD", "НИЖНИЙ": "NOVGOROD", 
    "НЖН": "NOVGOROD", "НИЖ": "NOVGOROD", "НИЖНОВ": "NOVGOROD", "ННОВ": "NOVGOROD",
}
# ========== РАБОТА С ПОЛЬЗОВАТЕЛЯМИ ==========
def load_users():
    """Загружает список всех пользователей, которые писали в группу"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_user(user):
    """Сохраняет или обновляет информацию о пользователе"""
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

# ========== СТАТИСТИКА ПО ТЕКУЩЕМУ СПИСКУ ==========
def load_list_stats():
    """Загружает статистику по текущему списку"""
    if os.path.exists(LIST_STATS_FILE):
        with open(LIST_STATS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "created_at": None,
        "created_by": None,
        "active_users": [],  # кто записывал в этот список
        "entries_count": 0
    }

def save_list_stats(stats):
    """Сохраняет статистику по текущему списку"""
    with open(LIST_STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

def reset_list_stats(creator_id=None):
    """Сбрасывает статистику для нового списка"""
    stats = {
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "created_by": creator_id,
        "active_users": [],
        "entries_count": 0
    }
    save_list_stats(stats)
    return stats

def add_to_list_stats(user_id):
    """Добавляет пользователя в статистику текущего списка"""
    stats = load_list_stats()
    if user_id not in stats["active_users"]:
        stats["active_users"].append(user_id)
    stats["entries_count"] += 1
    save_list_stats(stats)

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

async def check_private_access(update: Update):
    if update.message.chat.type != "private":
        return True
    if update.effective_user.id == OWNER_ID:
        return True
    await update.message.reply_text("⛔ Бот доступен только в группе")
    return False

def format_list():
    lines = []
    for server in SERVERS:
        if servers_data.get(server):
            lines.append(f"{server}  • {servers_data[server]}")
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

# ========== ОБРАБОТЧИК ВСЕХ СООБЩЕНИЙ (СБОР ПОЛЬЗОВАТЕЛЕЙ) ==========
async def track_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отслеживает всех пользователей, которые пишут в группу"""
    if update.message and update.message.chat.type in ["group", "supergroup"]:
        user = update.effective_user
        if user and not user.is_bot:
            save_user(user)

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
    
    add_to_list_stats(user.id)
    
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

# ========== ИСПРАВЛЕННАЯ КОМАНДА НОВОГО СПИСКА (СТАРЫЙ СПИСОК ОСТАЁТСЯ) ==========
async def new_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Создаёт новый чистый список и закрепляет его (только для владельца)"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Только для владельца")
        return
    
    # Очищаем все записи
    for server in SERVERS:
        servers_data[server] = ""
    save_data()
    
    # Удаляем старый ID сообщения
    if os.path.exists(MESSAGE_ID_FILE):
        os.remove(MESSAGE_ID_FILE)
    
    # Сбрасываем статистику для нового списка
    reset_list_stats(update.effective_user.id)
    
    await update.message.reply_text("📋 Создаю новый чистый список...")
    
    full_text = format_list()
    
    try:
        # Отправляем новое сообщение
        sent_message = await context.bot.send_message(chat_id=CHAT_ID, text=full_text)
        
        # Закрепляем новое сообщение (старое открепится автоматически)
        try:
            await context.bot.pin_chat_message(
                chat_id=CHAT_ID,
                message_id=sent_message.message_id,
                disable_notification=True
            )
            await update.message.reply_text(f"✅ Новый список создан и закреплён! Старый список остался в чате.")
        except Exception as e:
            await update.message.reply_text(f"✅ Новый список создан, но не удалось закрепить: {e}")
        
        # Сохраняем новый ID
        save_message_id(sent_message.message_id)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при создании списка: {e}")

# ========== КОМАНДА СТАТИСТИКИ ==========
async def list_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает статистику по текущему закреплённому списку (только для владельца)"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Только для владельца")
        return
    
    stats = load_list_stats()
    all_users = load_users()
    
    if not stats.get("created_at"):
        await update.message.reply_text("📭 Статистика по текущему списку отсутствует. Создайте новый список через /newlist")
        return
    
    # Получаем реальное количество участников в группе
    total_members = 0
    try:
        total_members = await context.bot.get_chat_member_count(chat_id=CHAT_ID)
    except Exception as e:
        logging.warning(f"Не удалось получить количество участников: {e}")
    
    # Получаем информацию о создателе
    creator_info = "Неизвестно"
    if stats["created_by"]:
        user_id_str = str(stats["created_by"])
        if user_id_str in all_users:
            user = all_users[user_id_str]
            creator_info = f"@{user['username']}" if user['username'] else user['first_name']
        else:
            creator_info = f"ID {stats['created_by']}"
    
    # Формируем ответ
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
    
    # Кто записывал
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
    
    # Кто не записывал
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

# ========== КОМАНДА СКАНИРОВАНИЯ ==========
async def scan_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Активно собирает информацию об участниках (только для владельца)"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Только для владельца")
        return
    
    await update.message.reply_text("🔍 Начинаю сбор информации об участниках...")
    
    try:
        total = await context.bot.get_chat_member_count(chat_id=CHAT_ID)
        
        chat = await context.bot.get_chat(chat_id=CHAT_ID)
        administrators = await chat.get_administrators()
        
        users_before = len(load_users())
        admins_added = 0
        
        all_users = load_users()
        for admin in administrators:
            if not admin.user.is_bot:
                user_id = str(admin.user.id)
                if user_id not in all_users:
                    all_users[user_id] = {
                        "id": admin.user.id,
                        "username": admin.user.username,
                        "first_name": admin.user.first_name,
                        "last_name": admin.user.last_name,
                        "last_seen": "администратор"
                    }
                    admins_added += 1
        
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_users, f, ensure_ascii=False, indent=2)
        
        users_after = len(all_users)
        
        await update.message.reply_text(
            f"✅ **Результаты сканирования:**\n"
            f"• Всего в группе: {total} участников\n"
            f"• Было в базе: {users_before}\n"
            f"• Добавлено администраторов: {admins_added}\n"
            f"• Стало в базе: {users_after}\n"
            f"• Осталось собрать: {total - users_after}\n\n"
            f"💡 Чтобы собрать остальных, попросите их написать в чат"
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при сканировании: {e}")

# ========== АВТОМАТИЧЕСКИЙ NEWLIST ==========
async def auto_newlist(context: ContextTypes.DEFAULT_TYPE):
    """Автоматически создает новый список"""
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
    
    application.add_handler(MessageHandler(filters.ALL, track_users), group=-1)
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("i", add_entry))
    application.add_handler(CommandHandler("list", list_entries))
    application.add_handler(CommandHandler("clear", clear_data))
    application.add_handler(CommandHandler("newlist", new_list))
    application.add_handler(CommandHandler("logs", show_logs))
    application.add_handler(CommandHandler("stats", list_stats))
    application.add_handler(CommandHandler("scan", scan_members))
    
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


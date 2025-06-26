# This script is a Telegram bot that provides currency, gold, and cryptocurrency prices.
# Coded By 💖 By ReZNuM

import logging
import requests
import pytz
import telebot
import jdatetime
import datetime
import convertdate.islamic
import json
import random
import os
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# Add Logging Configuration for better debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logging.Formatter.converter = lambda *args: datetime.datetime.now(pytz.timezone('Asia/Tehran')).timetuple()

# The Variable Inforamtions 
TOKEN = "Your Bot Token"
bot = telebot.TeleBot(TOKEN)
majid_api_key = 'Get it from @MajidAPI'
blocked_users = set()
ADMIN_USER_IDS = [123456789]  # Replace with actual admin user IDs
USERS_FILE = "users.json"

# Function For Save users in a JSON File for later if you want to send the users that have started the bot
def save_user(user_id, username):
    users = []
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                users = json.load(f)
        except json.JSONDecodeError:
            logger.error("Failed to read users.json, starting with empty list")
    
    if not any(user['id'] == user_id for user in users):
        users.append({"id": user_id, "username": username if username else "ندارد"})
        try:
            with open(USERS_FILE, 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=4)
            logger.info(f"Saved user {user_id} to users.json")
        except Exception as e:
            logger.error(f"Error saving user {user_id} to users.json: {e}")

# Manage Command that have to start with (/ , slash) in Telegram UI
commands = [
    telebot.types.BotCommand("start", "شروع ربات"),
    telebot.types.BotCommand("stats", "دریافت قیمت های مهم"),
    telebot.types.BotCommand("help", "نمایش دستورات قابل انجام ربات")
]
bot.set_my_commands(commands)

# Dictionary for daily Zekr (remembrance) based on the day of the week
zekr_dict = {
    "Saturday": "☀️ یا رَبَّ الْعالَمین",
    "Sunday": "🌿 یا ذَالجَلالِ وَالإکرام",
    "Monday": "🌙 یا قاضِیَ الْحاجات",
    "Tuesday": "✨ یا اَرحَمَ الرّاحِمین",
    "Wednesday": "🔥 یا حَیُّ یا قَیّوم",
    "Thursday": "🌊 لا اِلهَ اِلّا اللهُ الْمَلِکُ الْحَقُّ الْمبین",
    "Friday": "🕌 اللّهُمَّ صَلِّ عَلی مُحَمَّد وَ آلِ مُحَمَّد"
}

# Persian weekdays and months
weekdays_fa = {
    "Saturday": "شنبه",
    "Sunday": "یک‌شنبه",
    "Monday": "دوشنبه",
    "Tuesday": "سه‌شنبه",
    "Wednesday": "چهارشنبه",
    "Thursday": "پنج‌شنبه",
    "Friday": "جمعه"
}

# Persian months
persian_months = {
    1: "فروردین",
    2: "اردیبهشت",
    3: "خرداد",
    4: "تیر",
    5: "مرداد",
    6: "شهریور",
    7: "مهر",
    8: "آبان",
    9: "آذر",
    10: "دی",
    11: "بهمن",
    12: "اسفند"
}

# Islamic months
islamic_months = {
    1: "محرم",
    2: "صفر",
    3: "ربیع‌الاول",
    4: "ربیع‌الثانی",
    5: "جمادی‌الاول",
    6: "جمادی‌الثانی",
    7: "رجب",
    8: "شعبان",
    9: "رمضان",
    10: "شوال",
    11: "ذوالقعدة",
    12: "ذوالحجه"
}

bot_start_time = datetime.datetime.now(pytz.timezone('Asia/Tehran')).timestamp()

# Verification Function That checks if a message in the offline time of the bot is send or not , if yes , ignore it !
def is_message_valid(message):
    message_time = message.date
    logger.info(f"Checking message timestamp: {message_time} vs bot_start_time: {bot_start_time}")
    if message_time < bot_start_time:
        logger.warning(f"Ignoring old message from user {message.chat.id} sent at {message_time}")
        return False
    return True

# Functions For different form of numbers that is used in the code for better experience
def format_number(number):
    if isinstance(number, str):
        return number
    elif isinstance(number, (int, float)):
        return "{:,.0f}".format(number).replace(",", ",")
    else:
        return str(number)

def format_number_ashar(number):
    return "{:,.2f}".format(number).replace(",", ",")

def format_number_not(number):
    return "{:,.5f}".format(number).replace(",", ",")

def format_number_decimal(number):
    if number is None:
        return "ناموجود"
    if isinstance(number, str):
        try:
            number = float(number.replace(',', ''))
        except ValueError:
            return "ناموجود"
    if isinstance(number, (int, float)):
        return "{:,.3f}".format(number).replace(",", ",")
    return str(number)

# Function for get daily hadithes from hadith.json file that it shows one in a whole day for every user
def get_daily_hadith():
    try:
        with open('hadith.json', 'r', encoding='utf-8') as file:
            hadiths = json.load(file)
        
        iran_timezone = pytz.timezone('Asia/Tehran')
        j_date = jdatetime.datetime.now(iran_timezone).date()
        seed = int(f"{j_date.year}{j_date.month:02d}{j_date.day:02d}")
        random.seed(seed)
        
        selected_hadith = random.choice(hadiths)
        logger.info(f"Daily hadith selected for {j_date}: {selected_hadith['farsi'][:50]}...")
        return {
            'farsi': selected_hadith.get('farsi', 'حدیث یافت نشد'),
            'naghlfa': selected_hadith.get('naghlfa', 'نقل‌کننده مشخص نیست').rstrip(':').strip(),
            'source': selected_hadith.get('source', 'منبع مشخص نیست')
        }
    except FileNotFoundError:
        logger.error("File hadith.json not found")
        return {
            'farsi': 'حدیث یافت نشد',
            'naghlfa': 'نقل‌کننده مشخص نیست',
            'source': 'منبع مشخص نیست'
        }
    except Exception as e:
        logger.error(f"Error reading hadith: {e}")
        return {
            'farsi': 'حدیث یافت نشد',
            'naghlfa': 'نقل‌کننده مشخص نیست',
            'source': 'منبع مشخص نیست'
        }

# Get currencies from api.majidapi.ir 
def get_currency_prices():
    url = 'https://api.majidapi.ir/price/bonbast?token=' + majid_api_key
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        currencies = data['result']['currencies']
        
        currency_data = {}
        for item in currencies:
            if item['code'] in ['USD', 'EUR', 'AUD', 'CAD', 'TRY', 'RUB', 'AED', 'KWD']:
                currency_data[item['code']] = int(item['sell'].replace(',', ''))
        
        usd = currency_data.get('USD', 0)
        euro = currency_data.get('EUR', 0)
        aud = currency_data.get('AUD', 0)
        cad = currency_data.get('CAD', 0)
        tryy = currency_data.get('TRY', 0)
        rub = currency_data.get('RUB', 0)
        aed = currency_data.get('AED', 0)
        kwd = currency_data.get('KWD', 0)
        
        logger.info("Successfully fetched currency prices")
        return usd, euro, aud, cad, tryy, rub, aed, kwd
    except requests.RequestException as e:
        logger.error(f"Error fetching currency prices: {e}")
        return None, None, None, None, None, None, None, None

# Get Gold prices from api.majidapi.ir
def get_gold_prices():
    url = 'https://api.majidapi.ir/price/bonbast?token=' + majid_api_key
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        try:
            gold_18ayar = data['result']['gold']['gram']
        except (KeyError, TypeError):
            logger.error("Key 'gram' not found in gold data")
            gold_18ayar = None
        
        try:
            coins = {item['coin']: item['sell'] for item in data['result']['coins']}
            gold_bahar = coins.get('Emami', None)
            gold_nim = coins.get('&#189; Azadi', None)
            gold_rob = coins.get('&#188; Azadi', None)
            gold_gerami = coins.get('Gerami', None)
            
            if any(x is None for x in [gold_bahar, gold_nim, gold_rob, gold_gerami]):
                logger.warning(f"Some coins not found in API data: {coins}")
        except (KeyError, TypeError):
            logger.error("Key 'coins' or 'sell' not found in data")
            gold_bahar = gold_nim = gold_rob = gold_gerami = None
        
        logger.info("Successfully fetched gold prices")
        return gold_18ayar, gold_bahar, gold_nim, gold_rob, gold_gerami
    except requests.RequestException as e:
        logger.error(f"Error fetching gold prices: {e}")
        return None, None, None, None, None

# Get Crypto prices from api.majidapi.ir
def get_crypto_prices(symbols=None):
    url = 'https://api.majidapi.ir/price/bitpin?token=' + majid_api_key
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        markets = data['result']
        
        # check that user have given any symbol or not 
        if symbols is None:
            symbols = ['BTC', 'ETH', 'TON', 'NOT', 'TRX']
        
        crypto_data = {symbol: {'price_irt': None, 'price_usdt': None} for symbol in symbols}
        
        usdt_irt = None
        for market in markets:
            if market['code'] == 'USDT_IRT':
                usdt_irt = float(market['price'].replace(',', '')) if market['price'] else None
                break
        
        for market in markets:
            code = market['code']
            price = market['price'].replace(',', '') if market['price'] else None
            
            for symbol in symbols:
                if code == f"{symbol}_IRT":
                    crypto_data[symbol]['price_irt'] = float(price) if price else None
                elif code == f"{symbol}_USDT":
                    crypto_data[symbol]['price_usdt'] = float(price) if price else None
        
        logger.info(f"Successfully fetched crypto prices for {symbols}")
        return crypto_data, usdt_irt
    except requests.RequestException as e:
        logger.error(f"Error fetching crypto prices: {e}")
        return None, None

# Function For button (قیمت ارز)
def send_currency_price(user_id):
    logger.info(f"Sending currency prices to user {user_id}")
    usd, euro, aud, cad, tryy, rub, aed, kwd = get_currency_prices()
    iran_timezone = pytz.timezone('Asia/Tehran')
    g_date = datetime.datetime.now(iran_timezone)
    g_day = g_date.strftime("%A")
    g_month = g_date.strftime("%B")
    g_day_num = g_date.strftime("%d")
    g_year = g_date.strftime("%Y")
    j_date = jdatetime.datetime.fromgregorian(datetime=g_date)
    j_day = weekdays_fa[g_day]
    j_month = persian_months[j_date.month]
    j_day_num = j_date.day
    j_year = j_date.year
    islamic_date = convertdate.islamic.from_gregorian(g_date.year, g_date.month, g_date.day)
    i_day = islamic_date[2]
    i_month = islamic_months[islamic_date[1]]
    i_year = islamic_date[0]
    iran_hour = g_date.strftime("%H")
    iran_minute = g_date.strftime("%M")

    message = f"""
📅 تاریخ‌:
☀️| {j_day}
🌞| {j_day_num} {j_month} {j_year}
🕰 ساعت: {iran_hour}:{iran_minute} (به وقت ایران)

💵 نرخ ها :

💲 | دلار آمریکا: {format_number(usd)} تومان
💷 | دلار استرالیا: {format_number(aud)} تومان
💶 | یورو : {format_number(euro)} تومان
💸 | دلار کانادا : {format_number(cad)} تومان
💷 | درهم امارات   : {format_number(aed)} تومان
💴 | لیر ترکیه : {format_number(tryy)} تومان
💰 | روبل روسیه   : {format_number(rub)} تومان
💶 | دینار کویت    : {format_number(kwd)} تومان

ساخته شده با ❤️ توسط ReZNuM
    """
    bot.send_message(user_id, message, parse_mode="Markdown")
    logger.info(f"Currency prices sent to user {user_id}")

# Function For button (قیمت طلا و سکه)
def send_gold_price(user_id):
    logger.info(f"Sending gold prices to user {user_id}")
    gold_18ayar, gold_bahar, gold_nim, gold_rob, gold_gerami = get_gold_prices()
    iran_timezone = pytz.timezone('Asia/Tehran')
    g_date = datetime.datetime.now(iran_timezone)
    g_day = g_date.strftime("%A")
    g_month = g_date.strftime("%B")
    g_day_num = g_date.strftime("%d")
    g_year = g_date.strftime("%Y")
    j_date = jdatetime.datetime.fromgregorian(datetime=g_date)
    j_day = weekdays_fa[g_day]
    j_month = persian_months[j_date.month]
    j_day_num = j_date.day
    j_year = j_date.year
    islamic_date = convertdate.islamic.from_gregorian(g_date.year, g_date.month, g_date.day)
    i_day = islamic_date[2]
    i_month = islamic_months[islamic_date[1]]
    i_year = islamic_date[0]
    iran_hour = g_date.strftime("%H")
    iran_minute = g_date.strftime("%M")

    message = f"""
📅 تاریخ‌:  {j_day_num} {j_month} {j_year}
☀️| {j_day}
🕰 ساعت: {iran_hour}:{iran_minute} (به وقت ایران)

💵 قیمت‌ها:

🪙 | طلای ۱۸ عیار: {format_number(gold_18ayar)} تومان
🥇 | سکه تمام بهار: {format_number(gold_bahar)} تومان
🌓 | نیم سکه: {format_number(gold_nim)} تومان
🌜 | ربع سکه: {format_number(gold_rob)} تومان
🪙 | طلای گرمی : {format_number(gold_gerami)} تومان

ساخته شده با ❤️ توسط ReZNuM
    """
    bot.send_message(user_id, message, parse_mode="Markdown")
    logger.info(f"Gold prices sent to user {user_id}")

# Function For button (قیمت ارز دیجیتال)
def send_crypto_price(user_id):
    logger.info(f"Sending crypto prices to user {user_id}")
    crypto_data, usdt_irt = get_crypto_prices()
    iran_timezone = pytz.timezone('Asia/Tehran')
    g_date = datetime.datetime.now(iran_timezone)
    g_day = g_date.strftime("%A")
    j_date = jdatetime.datetime.fromgregorian(datetime=g_date)
    j_day = weekdays_fa[g_day]
    j_month = persian_months[j_date.month]
    j_day_num = j_date.day
    j_year = j_date.year
    iran_hour = g_date.strftime("%H")
    iran_minute = g_date.strftime("%M")
    
    if crypto_data is None or usdt_irt is None:
        message = "❌ خطا در دریافت قیمت ارزهای دیجیتال"
        logger.error("Failed to fetch crypto prices")
    else:
        def format_price_irt(price_usdt, usdt_irt):
            if price_usdt and usdt_irt:
                return format_number(int(price_usdt * usdt_irt))
            return "ناموجود"
        
        def format_change(change):
            if change is not None:
                sign = "+" if change >= 0 else ""
                return f"{sign}{change:.2f}%"
            return "ناموجود"
        
        message = f"""
📅 تاریخ: {j_day_num} {j_month} {j_year}
☀️| {j_day}
🕰 ساعت: {iran_hour}:{iran_minute} (به وقت ایران)

💸 قیمت ارزهای دیجیتال:

📈 بیت‌کوین (BTC):
💵 {format_price_irt(crypto_data['BTC']['price_usdt'], usdt_irt)} تومان
💲 {format_number(crypto_data['BTC']['price_usdt'])} دلار

📈 اتریوم (ETH):
💵 {format_price_irt(crypto_data['ETH']['price_usdt'], usdt_irt)} تومان
💲 {format_number(crypto_data['ETH']['price_usdt'])} دلار

📈 تون‌کوین (TON):
💵 {format_price_irt(crypto_data['TON']['price_usdt'], usdt_irt)} تومان
💲 {format_number_ashar(crypto_data['TON']['price_usdt'])} دلار

📈 نات‌کوین (NOT):
💵 {format_price_irt(crypto_data['NOT']['price_usdt'], usdt_irt)} تومان
💲 {format_number_not(crypto_data['NOT']['price_usdt'])} دلار

📈 ترون (TRX):
💵 {format_price_irt(crypto_data['TRX']['price_usdt'], usdt_irt)} تومان
💲 {format_number_not(crypto_data['TRX']['price_usdt'])} دلار

جهت دریافت قیمت ارزهای دیگر، نماد ارزها را وارد کنید (مثال: XRP یا NOT,XRP,BTC).
جهت برگشتن به منوی اصلی دستور /start را وارد کنید.

ساخته شده با ❤️ توسط ReZNuM
"""
    
    bot.send_message(user_id, message, parse_mode="Markdown")
    logger.info(f"Crypto prices sent to user {user_id}")

# Function For button (قیمت های مهم)
def send_price(user_id):
    logger.info(f"Sending important prices to user {user_id}")
    usd, euro, aud, cad, tryy, rub, aed, kwd = get_currency_prices()
    gold_18ayar, gold_bahar, gold_nim, gold_rob, gold_gerami = get_gold_prices()
    crypto_data, usdt_irt = get_crypto_prices()
    
    iran_timezone = pytz.timezone('Asia/Tehran')
    g_date = datetime.datetime.now(iran_timezone)
    g_day = g_date.strftime("%A")
    g_month = g_date.strftime("%B")
    g_day_num = g_date.strftime("%d")
    g_year = g_date.strftime("%Y")
    j_date = jdatetime.datetime.fromgregorian(datetime=g_date)
    j_day = weekdays_fa[g_day]
    j_month = persian_months[j_date.month]
    j_day_num = j_date.day
    j_year = j_date.year
    islamic_date = convertdate.islamic.from_gregorian(g_date.year, g_date.month, g_date.day)
    i_day = islamic_date[2]
    i_month = islamic_months[islamic_date[1]]
    i_year = islamic_date[0]
    iran_hour = g_date.strftime("%H")
    iran_minute = g_date.strftime("%M")
    
    daily_hadith = get_daily_hadith()
    
    btc_price_irt = format_number(int(crypto_data['BTC']['price_usdt'] * usdt_irt)) if crypto_data and usdt_irt and crypto_data['BTC']['price_usdt'] else "ناموجود"
    btc_price_usdt = format_number(crypto_data['BTC']['price_usdt']) if crypto_data and crypto_data['BTC']['price_usdt'] else "ناموجود"
    
    message = f"""
📅 تاریخ‌ها:
☀️| روز هفته: {j_day} ({g_day})
🌞| تاریخ شمسی: {j_day_num} {j_month} {j_year}
⛪| تاریخ میلادی: {g_month} {g_day_num} {g_year}
🐫| تاریخ قمری: {i_day} {i_month} {i_year}

🕰 ساعت: {iran_hour}:{iran_minute} (به وقت ایران)

💲| قیمت دلار (تومان): {format_number(usd)} تومان

💰 قیمت طلا و سکه:
🪙| طلای ۱۸ عیار: {format_number(gold_18ayar)} تومان
🥇| سکه تمام بهار: {format_number(gold_bahar)} تومان

💸 قیمت بیت‌کوین (BTC):
💵 {btc_price_irt} تومان
💲 {btc_price_usdt} دلار

📿 ذکر روز:
{zekr_dict[g_day]}

📜 حدیث روز:
{daily_hadith['farsi']}\n
🗣 نقل از: {daily_hadith['naghlfa']}\n
📚 منبع: {daily_hadith['source']}

ساخته شده با ❤️ توسط ReZNuM
"""
    bot.send_message(user_id, message, parse_mode="Markdown")
    logger.info(f"Important prices sent to user {user_id}")

# Handler of /start command 
@bot.message_handler(commands=['start'])
def start(message):
    if not is_message_valid(message):
        return
    user_id = message.chat.id
    username = message.from_user.username
    logger.info(f"Start command received from user {user_id}")

    save_user(user_id, username)

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_currency = telebot.types.KeyboardButton("نرخ ارز 💲")
    btn_gold_coin = telebot.types.KeyboardButton("نرخ طلا و سکه 💰")
    btn_crypto = telebot.types.KeyboardButton("قیمت ارز دیجیتال 💸")
    btn_imp = telebot.types.KeyboardButton("قیمت های مهم ❗")
    
    if user_id in ADMIN_USER_IDS:
        btn_special = telebot.types.KeyboardButton("پیام همگانی 📢")
    else:
        btn_special = telebot.types.KeyboardButton("ارتباط با پشتیبانی 📞")
    
    markup.add(btn_currency, btn_gold_coin, btn_crypto, btn_imp, btn_special)
    
    bot.send_message(user_id, """
سلام! 🎊 به ربات اعلام نرخ خوش اومدی 😊
این ربات برای نمایش نرخ ارز، طلا و سکه و ارزهای دیجیتال ساخته شده.
برای شروع ربات روی /start کلیک کن
در ضمن اگه به راهنمایی بیشتری نیاز داری روی /help کلیک کن
برای ارسال نظر یا مشکل، از دکمه ارتباط با پشتیبانی استفاده کن!

امیدوارم لحظات خوبی داشته باشی! 🌟
    """, parse_mode="Markdown", reply_markup=markup)
    logger.info(f"Keyboard menu sent to user {user_id}")

### Handlers for InlineMarkup Buttons ###

@bot.message_handler(func=lambda message: message.text == "نرخ طلا و سکه 💰")
def gold_nerkh(message):
    if not is_message_valid(message):
        return
    user_id = message.chat.id
    logger.info(f"Gold price command received from user {user_id}")
    send_gold_price(user_id)

@bot.message_handler(func=lambda message: message.text == "قیمت های مهم ❗")
def crypto_price(message):
    if not is_message_valid(message):
        return
    user_id = message.chat.id
    logger.info(f"Important prices command received from user {user_id}")
    send_price(user_id)

@bot.message_handler(func=lambda message: message.text == "نرخ ارز 💲")
def currency_nerkh(message):
    if not is_message_valid(message):
        return
    user_id = message.chat.id
    logger.info(f"Currency price command received from user {user_id}")
    send_currency_price(user_id)

@bot.message_handler(func=lambda message: message.text == "قیمت ارز دیجیتال 💸")
def crypto_nerkh(message):
    if not is_message_valid(message):
        return
    user_id = message.chat.id
    logger.info(f"Crypto price command received from user {user_id}")
    send_crypto_price(user_id)

@bot.message_handler(func=lambda message: message.text == "ارتباط با پشتیبانی 📞")
def handle_support(message):
    if not is_message_valid(message):
        return
    user_id = message.chat.id  
    if user_id in blocked_users:
        bot.send_message(user_id, "شما توسط ادمین بلاک شدید و نمی‌تونید پیام بفرستید 😕")
        return
    if user_id in ADMIN_USER_IDS:
        bot.send_message(user_id, "ادمین گرامی، شما نمی‌تونید به خودتون پیام پشتیبانی بفرستید! 😅")
        return
    logger.info(f"Support request initiated by user {user_id}")
    bot.send_message(user_id, "لطفاً نظر یا پیام خودتون رو برای پشتیبانی بنویسید، ما به زودی بررسی می‌کنیم 😊")
    bot.register_next_step_handler(message, forward_support_message)

# Function For forward support messages
def forward_support_message(message):
    if not is_message_valid(message):
        return
    user_id = message.chat.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name or ""
    full_name = f"{first_name} {last_name}".strip()

    logger.info(f"Support message received from user {user_id}")
    try:
        bot.forward_message(ADMIN_USER_IDS[0], user_id, message.message_id)
        keyboard = [
            [InlineKeyboardButton("جوابشو بده ✅", callback_data=f"reply_{user_id}")],
            [InlineKeyboardButton("بلاکه بلاک ❌", callback_data=f"block_{user_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(
            ADMIN_USER_IDS[0],
            f"""
📩 پیام پشتیبانی جدید:
👤 نام: {full_name}
🆔 آیدی: {user_id}
📧 یوزرنیم: @{username if username else 'ندارد'}
📝 پیام: (فوروارد شده)
            """,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        bot.send_message(user_id, "پیام شما به پشتیبانی ارسال شد ✅\nصبر کنید تا بررسی بشه")
    except Exception as e:
        logger.error(f"Error forwarding support message from user {user_id}: {e}")
        bot.send_message(user_id, "❌ خطایی در ارسال پیام رخ داد. لطفاً دوباره تلاش کنید.")

@bot.message_handler(func=lambda message: message.text == "پیام همگانی 📢")
def handle_broadcast(message):
    if not is_message_valid(message):
        return
    user_id = message.chat.id
    if user_id not in ADMIN_USER_IDS:
        bot.send_message(user_id, "این قابلیت فقط برای ادمین‌ها در دسترسه!")
        return
    logger.info(f"Broadcast initiated by admin {user_id}")
    bot.send_message(user_id, "هر پیامی که می‌خوای بنویس تا برای همه کاربران ارسال بشه 📢")
    bot.register_next_step_handler(message, send_broadcast)

def send_broadcast(message):
    if not is_message_valid(message):
        return
    user_id = message.chat.id
    if user_id not in ADMIN_USER_IDS:
        return
    users = []
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                users = json.load(f)
        except json.JSONDecodeError:
            logger.error("Failed to read users.json")
            bot.send_message(user_id, "❌ خطا در خواندن لیست کاربران!")
            return

    success_count = 0
    for user in users:
        if user["id"] in blocked_users:
            continue
        try:
            bot.send_message(user["id"], message.text)
            success_count += 1
        except Exception as e:
            logger.warning(f"Failed to send broadcast to user {user['id']}: {e}")
            continue
    bot.send_message(user_id, f"پیام به {success_count} کاربر ارسال شد 📢")
    logger.info(f"Broadcast sent to {success_count} users by admin {user_id}")

# Function That Admins use it for Answering back the messages of users
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user_id = call.from_user.id
    if user_id not in ADMIN_USER_IDS:
        bot.answer_callback_query(call.id, "این قابلیت فقط برای ادمین‌ها در دسترسه!")
        return
    
    action, target_user_id = call.data.split("_")
    target_user_id = int(target_user_id)
    
    if action == "reply":
        logger.info(f"Admin {user_id} initiated reply to user {target_user_id}")
        bot.answer_callback_query(call.id)
        bot.send_message(user_id, f"پاسخ خودتون رو برای کاربر {target_user_id} بنویسید:")
        bot.register_next_step_handler(call.message, send_support_reply, target_user_id)
    elif action == "block":
        logger.info(f"Admin {user_id} blocked user {target_user_id}")
        bot.answer_callback_query(call.id)
        bot.send_message(target_user_id, "شما توسط ادمین بلاک شدید و نمی‌تونید پیام بفرستید 😕")
        bot.edit_message_text(
            text=f"کاربر با آیدی {target_user_id} بلاک شد.",
            chat_id=user_id,
            message_id=call.message.message_id
        )

def send_support_reply(message, reply_to_user_id):
    if not is_message_valid(message):
        return
    user_id = message.chat.id
    if user_id not in ADMIN_USER_IDS:
        return
    try:
        bot.send_message(reply_to_user_id, f"پاسخ پشتیبانی: {message.text}")
        bot.send_message(user_id, f"پاسخ شما به کاربر {reply_to_user_id} ارسال شد ✅")
        logger.info(f"Support reply sent from admin {user_id} to user {reply_to_user_id}")
    except Exception as e:
        logger.error(f"Error sending support reply to user {reply_to_user_id}: {e}")
        bot.send_message(user_id, "❌ خطایی در ارسال پاسخ رخ داد. احتمالاً کاربر ربات رو بلاک کرده.")

@bot.message_handler(commands=['stats'])
def stats(message):
    if not is_message_valid(message):
        return
    user_id = message.chat.id
    logger.info(f"Stats command received from user {user_id}")
    send_price(user_id)

@bot.message_handler(commands=['alive'])
def alive(message):
    user_id = message.chat.id
    logger.info(f"Alive command received from user {user_id}")
    chat_type = message.chat.type
    if chat_type in ["private", "group", "supergroup"]:
        bot.send_message(user_id, "I'm alive and kicking! 🤖 RezStatsBot is here!")
        logger.info(f"Alive response sent to user {user_id}")

@bot.message_handler(commands=['help'])
def help(message):
    if not is_message_valid(message):
        return
    user_id = message.chat.id
    logger.info(f"Help command received from user {user_id}")
    bot.send_message(user_id, """
به بخش راهنمای ربات خوش اومدی 💖

دستورات موجود:
- /start: شروع ربات
- /stats: دریافت قیمت های مهم

زمانی هم که وارد بخش ارز های دیجیتال شدی ، میتونی اسم نماد موردنظرت رو بنویسی یا حتی چندین تا نماد رو با کاما جدا کنی (مثلا: BTC,ETH,TON) و قیمت اون ها رو ببینی.
برای دیدن قیمت‌ها، کافیه دستور /stats رو وارد کنی.
    """, parse_mode="Markdown")
    logger.info(f"Help response sent to user {user_id}")

@bot.message_handler(content_types=['text'])
def handle_crypto_symbols(message):
    if not is_message_valid(message):
        return
    user_id = message.chat.id
    if not is_message_valid(message):
        return
    user_id = message.chat.id
    if user_id in blocked_users:
        bot.send_message(user_id, "شما توسط ادمین بلاک شدید و نمی‌تونید پیام بفرستید 😕")
        return
    logger.info(f"Crypto symbols received from user {user_id}: {message.text}")
    
    symbols = [s.strip().upper() for s in message.text.split(',')]
    crypto_data, usdt_irt = get_crypto_prices(symbols)
    
    iran_timezone = pytz.timezone('Asia/Tehran')
    g_date = datetime.datetime.now(iran_timezone)
    g_day = g_date.strftime("%A")
    j_date = jdatetime.datetime.fromgregorian(datetime=g_date)
    j_day = weekdays_fa[g_day]
    j_month = persian_months[j_date.month]
    j_day_num = j_date.day
    j_year = j_date.year
    iran_hour = g_date.strftime("%H")
    iran_minute = g_date.strftime("%M")
    
    if crypto_data is None or usdt_irt is None:
        message_text = "❌ خطا در دریافت قیمت ارزهای دیجیتال"
        logger.error(f"Failed to fetch crypto prices for symbols: {symbols}")
    else:
        def format_price_irt(price_usdt, usdt_irt):
            if price_usdt and usdt_irt:
                return format_number(int(price_usdt * usdt_irt))
            return "ناموجود"
        
        message_text = f"""
📅 تاریخ: {j_day_num} {j_month} {j_year}
☀️| {j_day}
🕰 ساعت: {iran_hour}:{iran_minute} (به وقت ایران)
"""
        for symbol in symbols:
            if symbol in crypto_data:
                message_text += f"""
📈 {symbol}:
💵 {format_price_irt(crypto_data[symbol]['price_usdt'], usdt_irt)} تومان
💲 {format_number_decimal(crypto_data[symbol]['price_usdt'])} دلار
"""
            else:
                message_text += f"""
📈 {symbol}:
💵 ناموجود
💲 ناموجود
"""
                logger.warning(f"Symbol {symbol} not found in API data")
        
        message_text += """
جهت دریافت قیمت ارزهای دیگر، نماد ارزها را وارد کنید (مثال: XRP یا NOT,XRP,BTX).
جهت برگشتن به منوی اصلی دستور /start را وارد کنید.

ساخته شده با ❤️ توسط ReZNuM
"""
    
    bot.send_message(user_id, message_text, parse_mode="Markdown")
    logger.info(f"Custom crypto prices sent to user {user_id} for symbols: {symbols}")

if __name__ == '__main__':
    logger.info("Starting RezStatsBot")
    try:
        bot.polling()
    except Exception as e:
        logger.error(f"Bot stopped due to error: {e}")
        raise
import requests
import pytz
import telebot
import jdatetime
import datetime
import convertdate.islamic
import json
import random
 
TOKEN = "Your Bot Token Here"
bot = telebot.TeleBot(TOKEN)

majid_api_key = 'Take it From @MajidAPITokenBot in Telegram'

commands = [
    telebot.types.BotCommand("start", "شروع ربات"),
    telebot.types.BotCommand("stats", "دریافت قیمت های مهم"),
    telebot.types.BotCommand("help", "نمایش دستورات قابل انجام ربات")
]
bot.set_my_commands(commands)

zekr_dict = {
    "Saturday": "☀️ یا رَبَّ الْعالَمین",
    "Sunday": "🌿 یا ذَالجَلالِ وَالإکرام",
    "Monday": "🌙 یا قاضِیَ الْحاجات",
    "Tuesday": "✨ یا اَرحَمَ الرّاحِمین",
    "Wednesday": "🔥 یا حَیُّ یا قَیّوم",
    "Thursday": "🌊 لا اِلهَ اِلّا اللهُ الْمَلِکُ الْحَقُّ الْمبین",
    "Friday": "🕌 اللّهُمَّ صَلِّ عَلی مُحَمَّد وَ آلِ مُحَمَّد"
}

weekdays_fa = {
    "Saturday": "شنبه",
    "Sunday": "یک‌شنبه",
    "Monday": "دوشنبه",
    "Tuesday": "سه‌شنبه",
    "Wednesday": "چهارشنبه",
    "Thursday": "پنج‌شنبه",
    "Friday": "جمعه"
}

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

def get_daily_hadith():
    try:
        with open('hadith.json', 'r', encoding='utf-8') as file:
            hadiths = json.load(file)
        
        j_date = jdatetime.date.today()
        seed = int(f"{j_date.year}{j_date.month:02d}{j_date.day:02d}")
        random.seed(seed)
        
        selected_hadith = random.choice(hadiths)
        
        return {
            'farsi': selected_hadith.get('farsi', 'حدیث یافت نشد'),
            'naghlfa': selected_hadith.get('naghlfa', 'نقل‌کننده مشخص نیست')[:-2],
            'source': selected_hadith.get('source', 'منبع مشخص نیست')
        }
    except FileNotFoundError:
        print("hadith.json file not found.")
        return {
            'farsi': 'حدیث یافت نشد',
            'naghlfa': 'نقل‌کننده مشخص نیست',
            'source': 'منبع مشخص نیست'
        }
    except Exception as e:
        print(f"Error in reading Hadith: {e}")
        return {
            'farsi': 'حدیث یافت نشد',
            'naghlfa': 'نقل‌کننده مشخص نیست',
            'source': 'منبع مشخص نیست'
        }


def get_crypto_prices():
    url = 'https://api.majidapi.ir/price/bitpin?token=' + majid_api_key
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        markets = data['result']
        
        crypto_data = {
            'BTC': {'price_irt': None, 'price_usdt': None, 'change': None},
            'ETH': {'price_irt': None, 'price_usdt': None, 'change': None},
            'TON': {'price_irt': None, 'price_usdt': None, 'change': None},
            'NOT': {'price_irt': None, 'price_usdt': None, 'change': None},
            'TRX': {'price_irt': None, 'price_usdt': None, 'change': None}
        }
        
        usdt_irt = None
        for market in markets:
            if market['code'] == 'USDT_IRT':
                usdt_irt = float(market['price'].replace(',', '')) if market['price'] else None
                break
        
        for market in markets:
            code = market['code']
            price = market['price'].replace(',', '') if market['price'] else None
            
            for crypto in crypto_data:
                if code == f"{crypto}_IRT":
                    crypto_data[crypto]['price_irt'] = float(price) if price else None
                elif code == f"{crypto}_USDT":
                    crypto_data[crypto]['price_usdt'] = float(price) if price else None
        
        return crypto_data, usdt_irt
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None, None


def get_currency_prices():
    url = 'https://api.majidapi.ir/price/bonbast?token=' + majid_api_key
    response = requests.get(url)
    
    if response.status_code == 200:
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
        
        return usd, euro, aud, cad, tryy, rub, aed, kwd
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None, None, None, None, None, None, None, None

def send_crypto_price(user_id):
    crypto_data, usdt_irt = get_crypto_prices()
    g_date = datetime.datetime.now()
    g_day = g_date.strftime("%A")
    j_date = jdatetime.date.today()
    j_day = weekdays_fa[g_day]
    j_month = persian_months[j_date.month]
    j_day_num = j_date.day
    j_year = j_date.year
    iran_timezone = pytz.timezone('Asia/Tehran')
    iran_time = g_date.astimezone(iran_timezone)
    iran_hour = iran_time.strftime("%H")
    iran_minute = iran_time.strftime("%M")
    
    if crypto_data is None or usdt_irt is None:
        message = "❌ خطا در دریافت قیمت ارزهای دیجیتال"
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

ساخته شده با ❤️ توسط ReZNuM
"""
    
    bot.send_message(user_id, message, parse_mode="Markdown")

def get_gold_prices():
    url = 'https://api.majidapi.ir/price/bonbast?token=' + majid_api_key
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        gold_18ayar = data['result']['gold']['gram']  
        
        coins = {item['coin']: item['sell'] for item in data['result']['coins']}
        
        gold_bahar = coins['Emami'] 
        gold_nim = coins['&#189; Azadi'] 
        gold_rob = coins['&#188; Azadi'] 
        gold_gerami = coins['Gerami'] 
        
        return gold_18ayar, gold_bahar, gold_nim, gold_rob, gold_gerami
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None, None, None, None, None

def send_currency_price(user_id):
    usd, euro, aud, cad, tryy , rub, aed, kwd = get_currency_prices()
    g_date = datetime.datetime.now()
    g_day = g_date.strftime("%A")
    g_month = g_date.strftime("%B")
    g_day_num = g_date.strftime("%d")
    g_year = g_date.strftime("%Y")
    j_date = jdatetime.date.today()
    j_day = weekdays_fa[g_day]  
    j_month = persian_months[j_date.month] 
    j_day_num = j_date.day
    j_year = j_date.year
    islamic_date = convertdate.islamic.from_gregorian(g_date.year, g_date.month, g_date.day)
    i_day = islamic_date[2]
    i_month = islamic_months[islamic_date[1]]
    i_year = islamic_date[0]
    iran_timezone = pytz.timezone('Asia/Tehran')
    iran_time = g_date.astimezone(iran_timezone)
    iran_hour = iran_time.strftime("%H")
    iran_minute = iran_time.strftime("%M")

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


def send_gold_price(user_id):
    gold_18ayar, gold_bahar, gold_nim, gold_rob, gold_gerami = get_gold_prices()
    g_date = datetime.datetime.now()
    g_day = g_date.strftime("%A")
    g_month = g_date.strftime("%B")
    g_day_num = g_date.strftime("%d")
    g_year = g_date.strftime("%Y")
    j_date = jdatetime.date.today()
    j_day = weekdays_fa[g_day]  
    j_month = persian_months[j_date.month] 
    j_day_num = j_date.day
    j_year = j_date.year
    islamic_date = convertdate.islamic.from_gregorian(g_date.year, g_date.month, g_date.day)
    i_day = islamic_date[2]
    i_month = islamic_months[islamic_date[1]]
    i_year = islamic_date[0]
    iran_timezone = pytz.timezone('Asia/Tehran')
    iran_time = g_date.astimezone(iran_timezone)
    iran_hour = iran_time.strftime("%H")
    iran_minute = iran_time.strftime("%M")

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


def send_price(user_id):
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
⛪| تاریخ میلادی:  {g_month}  {g_day_num} {g_year}
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

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    bot.send_message(user_id, """
سلام!🎊 به ربات اعلام نرخ خوش اومدی 😊
این ربات برای نمایش نرخ ارز، طلا و سکه و ارزهای دیجیتال ساخته شده.
.برای شروع ربات روی  /start کلیک کن
.در ضمن اگه به راهنمایی بیشتری نیاز داری روی /help کلیک کن

امیدوارم لحظات خوبی داشته باشی! 🌟
    """, parse_mode="Markdown")

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_currency = telebot.types.KeyboardButton("نرخ ارز 💲")
    btn_gold_coin = telebot.types.KeyboardButton("نرخ طلا و سکه 💰")
    btn_crypto = telebot.types.KeyboardButton("قیمت ارز دیجیتال 💸")
    btn_imp = telebot.types.KeyboardButton("قیمت های مهم ❗")

    markup.add(btn_currency, btn_gold_coin, btn_crypto, btn_imp)
    bot.send_message(user_id, "در ضمن میتونی با کلیک کردن روی گزینه های زیر ، نرخ های موردنظرت رو ببینی", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "نرخ طلا و سکه 💰")
def gold_nerkh(message):
    user_id = message.chat.id
    send_gold_price(user_id)


@bot.message_handler(func=lambda message: message.text =="قیمت های مهم ❗")
def crypto_price(message):
    user_id = message.chat.id
    send_price(user_id)


@bot.message_handler(func=lambda message: message.text == "نرخ ارز 💲")
def currency_nerkh(message):
    user_id = message.chat.id
    send_currency_price(user_id)

@bot.message_handler(func=lambda message: message.text == "قیمت ارز دیجیتال 💸")
def crypto_nerkh(message):
    user_id = message.chat.id
    send_crypto_price(user_id)
  
@bot.message_handler(commands=['stats'])
def stats(message):
    user_id = message.chat.id
    send_price(user_id)

@bot.message_handler(commands=['alive'])
def alive(message):
    chat_type = message.chat.type
    if chat_type in ["private", "group", "supergroup"]:
        bot.send_message(message.chat.id, "I'm alive and kicking! 🤖 RezStatsBot is here!")
@bot.message_handler(commands=['help'])
def help(message):
    user_id = message.chat.id
    bot.send_message(user_id, """
به بخش راهنمای ربات خوش اومدی 💖

دستورات موجود:
- /start: شروع ربات
- /stats: دریافت قیمت های مهم 

برای دیدن قیمت‌ها، کافیه دستور /stats رو وارد کنی.
    """, parse_mode="Markdown")

if __name__ == '__main__':
    bot.polling()



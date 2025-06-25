# RezStatsBot 🤖

A Telegram bot for real-time prices of currencies, gold, cryptocurrencies, and daily Islamic content in Persian. 🌟

## Overview 📋

RezStatsBot is a Telegram bot designed to deliver up-to-date financial information and daily Islamic content to Persian-speaking users. It fetches data from the [Majid API](https://api.majidapi.ir) to provide prices for currencies (e.g., USD, EUR), gold, and cryptocurrencies (e.g., BTC, ETH, TON, NOT, TRX). Additionally, it displays daily Islamic hadiths, supplications (zekr), and Persian/Islamic/Gregorian calendar dates, all tailored to the Asia/Tehran timezone.

## Features 📊

- 💵 **Currency Prices**: Real-time prices of major currencies (USD, EUR, AUD, CAD, TRY, RUB, AED, KWD) in Iranian Rial (IRT).
- 🪙 **Gold and Coin Prices**: Prices for 18-carat gold and Iranian coins (e.g., Emami, Half Azadi).
- 💸 **Cryptocurrency Prices**: Prices for BTC, ETH, TON, NOT, and TRX in USD (with 3 decimal places) and IRT, including 24-hour change percentages.
- 📜 **Daily Islamic Content**:
  - A daily hadith with its source and narrator.
  - A daily zekr (supplication) based on the day of the week.
  - Persian (Jalali), Islamic (Hijri), and Gregorian calendar dates.
- 🎨 **User-Friendly Interface**: Interactive keyboard menu with options for currency, gold, crypto, and important prices.
- 🕰 **Timezone Support**: All dates and times are displayed in the Asia/Tehran timezone.

## Installation 🚀

### Prerequisites
- Python 3.8 or higher
- A Telegram bot token from [BotFather](https://t.me/BotFather)
- A valid API key from [Majid API](https://api.majidapi.ir)

### Steps
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/rezstatsbot.git
   cd rezstatsbot
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   - Create a `config.py` file or update `price.py` with your Telegram bot token and Majid API key:
     ```python
     TOKEN = "your-telegram-bot-token"
     majid_api_key = "your-majid-api-key"
     ```
   - Ensure `hadith.json` is present in the project root with the correct format for daily hadiths.

4. **Run the Bot**:
   ```bash
   python price.py
   ```

## Usage 📱

1. Start the bot by sending `/start` on Telegram.
2. Use the keyboard menu to select:
   - 💲 **نرخ ارز**: View currency prices.
   - 💰 **نرخ طلا و سکه**: Check gold and coin prices.
   - 💸 **قیمت ارز دیجیتال**: See cryptocurrency prices.
   - ❗ **قیمت‌های مهم**: Get key prices (USD, gold, BTC), daily zekr, hadith, and calendar dates.
3. Additional commands:
   - `/stats`: Same as "قیمت‌های مهم".
   - `/help`: Display available commands.
   - `/alive`: Check if the bot is running.

## Dependencies 🛠

The project dependencies are listed in `requirements.txt`. Install them using:
```bash
pip install -r requirements.txt
``` 

## Contributing 🤝

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

Please ensure your code follows PEP 8 guidelines and includes appropriate tests.

## Contact 📬

For questions or support, contact the developer:
- Telegram: @ItsReZNuM
- Email: rmohamadnia85@gmail.com

Built with ❤️ by ReZNuM
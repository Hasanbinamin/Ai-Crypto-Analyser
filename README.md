# 📊 Market Sentiment Analysis Bot

A Telegram bot that analyzes cryptocurrency market sentiment by monitoring trading activity, with a focus on distinguishing between retail and "whale" traders.

[![Docker](https://img.shields.io/badge/Docker-Supported-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?logo=telegram&logoColor=white)](https://telegram.org/)
[![Binance](https://img.shields.io/badge/Binance-API-F0B90B?logo=binance&logoColor=white)](https://www.binance.com/)

## 🌟 Features

- **Real-time Analysis**: Get instant market sentiment analysis for any cryptocurrency pair
- **Whale vs Retail**: Separate analysis for retail traders and large "whale" traders
- **Flexible Timeframes**: Analyze market sentiment over custom time periods
- **Automated Alerts**: Set up periodic analysis with configurable intervals
- **Docker Support**: Easy deployment with Docker and Docker Compose

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Telegram Bot Token from [@BotFather](https://t.me/botfather)
- Google API Key for Gemini AI

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Hasanbinamin/Ai-Crypto-Analyser.git
   cd market-sentiment-bot
   ```

2. Edit the `.env` file:

   In `.env` add your API keys:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   GOOGLE_API_KEY=your_google_api_key
   ```

3. Build and start the services:
   ```bash
   docker-compose up --build
   ```

## 🛠 Usage

1. Start a chat with your bot on Telegram
2. Use the menu to set your trading pair (e.g., BTCUSDT)
3. Set your preferred timeframe (e.g., 1h, 4h, 1d)
4. Save your signal or enable automatic analysis loops

### Available Commands

- `/start` - Show the main menu
- `Set Symbol` - Set the trading pair (e.g., BTCUSDT)
- `Set Timeframe` - Set analysis timeframe (e.g., 1h, 4h, 1d)
- `Save Signal` - Save your current settings
- `Resend Signal` - Get the latest analysis
- `Enable Loop` - Enable periodic analysis
- `Stop Loop` - Disable periodic analysis

## 📊 How It Works

The bot analyzes market sentiment by:
1. Fetching trade data from Binance
2. Separating trades into retail and whale categories
3. Calculating sentiment indices for each group
4. Using Google's Gemini AI to interpret the data
5. Providing actionable insights through Telegram

## 🐋 Whale Detection

Trades are classified as "whale" trades if their value exceeds $100,000. This threshold can be adjusted in the `tool.py` file.

## 🛠 Development

### Project Structure

```
.
├── bot.py            # Telegram bot implementation
├── api.py            # FastAPI server
├── agent.py          # Market analysis agent
├── tool.py           # Data processing and analysis
├── requirements.txt  # Python dependencies
└── data/             # Cached trade data
```

### Running Locally (Without Docker)

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the API server in one terminal:
   ```bash
   uvicorn api:app --reload
   ```

4. Start the bot in another terminal:
   ```bash
   python bot.py
   ```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Binance API](https://binance-docs.github.io/apidocs/spot/en/)
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Google Gemini](https://ai.google.dev/)

---

<div align="center">
  Made with ❤️ for crypto traders
</div>

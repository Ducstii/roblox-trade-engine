# 🎮 Roblox Trade Command Engine

An autonomous trading assistant for Roblox Limiteds that continuously scans market data, identifies profitable trade opportunities, and sends alerts via Discord.

## 🚀 Features

- **Continuous Market Scanning**: Automatically monitors Rolimons for Limited items
- **Intelligent Scoring**: Uses configurable weights and strategy modes (Sniper, Aggressive, Conservative, Momentum)
- **Trade Simulation**: Generates and evaluates trade combinations
- **Discord Alerts**: Automated notifications for high-quality trades
- **Comprehensive GUI**: Real-time monitoring with multiple tabs
- **Debug Interface**: Testing interface for all system endpoints

## 📋 Requirements

- Python 3.8+
- FastAPI
- aiohttp
- discord.py
- tkinter (for GUI)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd roblox-limited-scanner
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the application:
   - Edit `config/settings.json` to set your preferences
   - Add your Discord webhook URL for alerts

## 🚀 Usage

### Starting the Backend Server

```bash
python main.py
```

The FastAPI server will start on `http://localhost:8000`

### API Endpoints

- `GET /` - Root endpoint
- `GET /status` - System status and health metrics
- `GET /scan` - Run a Rolimons item scan
- `GET /top-picks` - Return top scored items
- `GET /combo` - Return best trade combinations
- `GET /timeline/{item_id}` - Item's historical data
- `POST /config` - Update configuration
- `POST /webhook` - Save Discord webhook configuration
- `GET /calendar` - Show forecasted trade windows
- `GET /risk-index` - Return current market volatility

### Strategy Modes

- **Sniper**: Favors undervalued items with high potential
- **Aggressive**: Targets high-volume, trending items
- **Conservative**: Focuses on stable, established items
- **Momentum**: Tracks items with recent price increases

## 📊 Configuration

The system uses a weighted scoring algorithm with the following components:

- **ROI Weight**: Return on Investment percentage
- **Demand Weight**: Item demand tier
- **Volume Weight**: Trade volume
- **Volatility Weight**: Price volatility
- **Engagement Weight**: Social engagement metrics
- **Trait Weight**: Item characteristics

## 🔧 Development

### Project Structure

```
├── main.py                 # FastAPI server
├── config/
│   ├── config_manager.py   # Configuration management
│   └── settings.json       # User settings
├── models/
│   └── data_models.py      # Pydantic data models
├── scraper/
│   └── rolimons_scraper.py # Rolimons API client
├── scoring/
│   └── score_engine.py     # Scoring algorithm
├── trade/
│   └── trade_simulator.py  # Trade combination generator
└── requirements.txt        # Python dependencies
```

### Adding New Features

1. Create new modules in appropriate directories
2. Update the main FastAPI server with new endpoints
3. Add configuration options if needed
4. Update the GUI to include new features

## 📈 Trading Strategy

The system analyzes items based on:

- **Market Data**: RAP, value, volume, demand
- **Social Signals**: Hype status, rarity, premium status
- **Technical Indicators**: Price volatility, momentum
- **Risk Assessment**: Volume, demand stability, market conditions

## 🔔 Discord Integration

Configure Discord webhooks to receive alerts for:

- High-profit trade opportunities
- Market trend changes
- System status updates
- Error notifications

## 🐛 Debug Mode

Use the debug interface to:

- Test all API endpoints
- Validate scoring algorithms
- Check system health
- Monitor performance metrics

## 📝 License

This project is for educational purposes. Please ensure compliance with Roblox's Terms of Service and API usage policies.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## ⚠️ Disclaimer

This tool is for educational and research purposes. Trading in Roblox Limiteds involves risk, and past performance does not guarantee future results. Always do your own research and trade responsibly.

---

**Built with ❤️ for the Roblox trading community** 
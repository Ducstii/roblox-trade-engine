# Roblox Trade Command Engine - GUI Client

A standalone GUI client for the Roblox Trade Command Engine backend.

## Features

- **Dashboard**: Real-time system status and top picks
- **Trade Console**: View and analyze trade combinations
- **Timeline**: Historical data for specific items
- **Strategy Config**: Adjust scoring weights and strategy modes
- **Calendar**: Forecasted trade windows
- **Alerts**: Discord webhook configuration and testing
- **Debug**: API endpoint testing and performance metrics

## Installation

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the GUI**:
   ```bash
   python launch_gui.py
   ```
   
   Or directly:
   ```bash
   python main.py
   ```

## Usage

### Connecting to Backend

1. Enter your backend URL in the "Backend URL" field (default: `http://localhost:8000`)
2. Click "Connect" to test the connection
3. The status indicator will show "Connected" in green when successful

### Running Scans

1. Click "Start Scan" to initiate a market scan
2. The scan runs in the background and updates all data automatically
3. Progress is shown in the status bar

### Configuration

- **Strategy Mode**: Choose between Conservative, Aggressive, Sniper, or Momentum
- **Scoring Weights**: Adjust the importance of different factors (ROI, Demand, Volume, etc.)
- **Discord Webhook**: Configure alerts for high-quality trades

### Debug Features

- Test individual API endpoints
- View response times and performance metrics
- Monitor system health and status

## Backend Requirements

The GUI client requires a running instance of the Roblox Trade Command Engine backend with the following endpoints:

- `GET /` - Health check
- `GET /status` - System status
- `GET /scan` - Start market scan
- `GET /top-picks` - Get top scored items
- `GET /combo` - Get trade combinations
- `GET /calendar` - Get forecast windows
- `GET /risk-index` - Get market volatility
- `POST /config` - Update configuration
- `POST /webhook` - Save Discord webhook
- `GET /test-discord` - Test Discord webhook

## Troubleshooting

### Connection Issues

- Ensure the backend server is running
- Check the backend URL is correct
- Verify the backend is accessible from your network

### Import Errors

- Install required dependencies: `pip install -r requirements.txt`
- Ensure you're using Python 3.7+

### GUI Issues

- The GUI uses Tkinter which is included with Python
- On some Linux systems, you may need to install tkinter: `sudo apt-get install python3-tk`

## File Structure

```
gui/
├── main.py              # Main GUI application
├── launch_gui.py        # Launcher script
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## License

This GUI client is part of the Roblox Trade Command Engine project. 
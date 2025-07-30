# Roblox Trade Command Engine - Deployment Guide

This guide will walk you through deploying the backend on your server and running the GUI client locally.

## 🖥️ Backend Server Setup

### Prerequisites

- **Server Requirements**:
  - Linux/Windows server with Python 3.8+
  - At least 2GB RAM
  - Stable internet connection
  - Port 8000 available (or configurable)

### Step 1: Server Preparation

1. **SSH into your server**:
   ```bash
   ssh username@your-server-ip
   ```

2. **Install Python and dependencies**:
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip python3-venv git

   # CentOS/RHEL
   sudo yum install python3 python3-pip git
   ```

3. **Create project directory**:
   ```bash
   mkdir -p /opt/roblox-trade-engine
   cd /opt/roblox-trade-engine
   ```

### Step 2: Backend Installation

1. **Clone or upload the backend code**:
   ```bash
   # Option 1: Git clone (if you have a repository)
   git clone https://github.com/your-repo/roblox-trade-engine.git .

   # Option 2: Upload files manually via SCP/SFTP
   # Upload all backend files to /opt/roblox-trade-engine/
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create necessary directories**:
   ```bash
   mkdir -p logs cache
   ```

### Step 3: Configuration

1. **Create environment file** (optional):
   ```bash
   cp .env.example .env
   # Edit .env with your specific settings
   ```

2. **Configure Discord webhook** (optional):
   - Create a Discord webhook in your server
   - Note the webhook URL for later configuration

### Step 4: Running the Backend

#### Option A: Direct Run (Development)
```bash
cd /opt/roblox-trade-engine
source venv/bin/activate
python main.py
```

#### Option B: Systemd Service (Production)
1. **Create service file**:
   ```bash
   sudo nano /etc/systemd/system/roblox-trade-engine.service
   ```

2. **Add service configuration**:
   ```ini
   [Unit]
   Description=Roblox Trade Command Engine
   After=network.target

   [Service]
   Type=simple
   User=your-username
   WorkingDirectory=/opt/roblox-trade-engine
   Environment=PATH=/opt/roblox-trade-engine/venv/bin
   ExecStart=/opt/roblox-trade-engine/venv/bin/python main.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start service**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable roblox-trade-engine
   sudo systemctl start roblox-trade-engine
   sudo systemctl status roblox-trade-engine
   ```

#### Option C: Docker (Alternative)
1. **Create Dockerfile**:
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   RUN mkdir -p logs cache
   
   EXPOSE 8000
   CMD ["python", "main.py"]
   ```

2. **Build and run**:
   ```bash
   docker build -t roblox-trade-engine .
   docker run -d -p 8000:8000 --name roblox-trade-engine roblox-trade-engine
   ```

### Step 5: Firewall Configuration

1. **Open port 8000**:
   ```bash
   # Ubuntu/Debian (ufw)
   sudo ufw allow 8000

   # CentOS/RHEL (firewalld)
   sudo firewall-cmd --permanent --add-port=8000/tcp
   sudo firewall-cmd --reload
   ```

2. **Test backend access**:
   ```bash
   curl http://your-server-ip:8000/
   # Should return: {"message": "Roblox Trade Command Engine", "version": "1.0.0", "status": "running"}
   ```

## 💻 GUI Client Setup (Local)

### Prerequisites

- **Local Requirements**:
  - Windows/Mac/Linux with Python 3.7+
  - Internet connection to reach your server

### Step 1: Download GUI Client

1. **Create local directory**:
   ```bash
   mkdir roblox-trade-gui
   cd roblox-trade-gui
   ```

2. **Copy GUI files**:
   - Copy the entire `gui/` folder from the project
   - Or download from your repository

### Step 2: Install Dependencies

```bash
# Windows
pip install -r gui/requirements.txt

# Mac/Linux
pip3 install -r gui/requirements.txt
```

### Step 3: Configure Connection

1. **Edit backend URL**:
   - Open `gui/main.py`
   - Change `self.backend_url = "http://localhost:8000"` to your server IP
   - Example: `self.backend_url = "http://your-server-ip:8000"`

2. **Or configure via GUI**:
   - Run the GUI and enter the backend URL in the interface

### Step 4: Run GUI Client

```bash
# Windows
python gui/main.py

# Mac/Linux
python3 gui/main.py
```

## 🔧 Configuration

### Backend Configuration

1. **Discord Webhook Setup**:
   ```bash
   # Via API
   curl -X POST http://your-server-ip:8000/webhook \
     -H "Content-Type: application/json" \
     -d '{
       "webhook_url": "https://discord.com/api/webhooks/your-webhook-url",
       "role_id": "your-role-id",
       "alert_threshold": 3500
     }'
   ```

2. **Strategy Configuration**:
   ```bash
   # Via API
   curl -X POST http://your-server-ip:8000/config \
     -H "Content-Type: application/json" \
     -d '{
       "strategy_mode": "aggressive",
       "scoring_weights": {
         "roi_weight": 0.4,
         "demand_weight": 0.3,
         "volume_weight": 0.2,
         "volatility_weight": 0.1
       }
     }'
   ```

### GUI Configuration

1. **Backend URL**: Enter your server's IP address and port
2. **Discord Webhook**: Configure in the Alerts tab
3. **Strategy Settings**: Adjust in the Strategy Config tab

## 🚀 Testing the Setup

### 1. Test Backend Connection
```bash
# From your local machine
curl http://your-server-ip:8000/status
```

### 2. Test Discord Integration
```bash
curl http://your-server-ip:8000/test-discord
```

### 3. Run a Test Scan
```bash
curl http://your-server-ip:8000/scan
```

### 4. Check Results
```bash
curl http://your-server-ip:8000/top-picks
curl http://your-server-ip:8000/combo
```

## 📊 Monitoring

### Backend Monitoring

1. **Check service status**:
   ```bash
   sudo systemctl status roblox-trade-engine
   ```

2. **View logs**:
   ```bash
   tail -f /opt/roblox-trade-engine/logs/app.log
   ```

3. **Monitor system resources**:
   ```bash
   htop
   df -h
   free -h
   ```

### GUI Monitoring

- Use the Debug tab to test endpoints
- Monitor connection status in the status bar
- Check auto-refresh functionality

## 🔒 Security Considerations

1. **Firewall**: Only open necessary ports
2. **HTTPS**: Consider using a reverse proxy with SSL
3. **Authentication**: Add API key authentication if needed
4. **Rate Limiting**: Implement rate limiting for API endpoints

## 🛠️ Troubleshooting

### Common Issues

1. **Connection Refused**:
   - Check if backend is running
   - Verify firewall settings
   - Check port configuration

2. **Import Errors**:
   - Ensure all dependencies are installed
   - Check Python version compatibility

3. **Discord Webhook Failures**:
   - Verify webhook URL is correct
   - Check Discord server permissions

4. **Scan Failures**:
   - Check internet connectivity
   - Verify Rolimons API access
   - Review error logs

### Log Locations

- **Backend logs**: `/opt/roblox-trade-engine/logs/app.log`
- **System logs**: `journalctl -u roblox-trade-engine`

### Support Commands

```bash
# Restart service
sudo systemctl restart roblox-trade-engine

# Check service logs
sudo journalctl -u roblox-trade-engine -f

# Test backend manually
cd /opt/roblox-trade-engine
source venv/bin/activate
python main.py
```

## 📈 Performance Optimization

1. **Server Resources**:
   - Monitor CPU and memory usage
   - Consider upgrading if needed

2. **Caching**:
   - The system uses GZIP caching for efficiency
   - Monitor cache size and cleanup

3. **Scan Frequency**:
   - Adjust scan intervals based on your needs
   - Consider rate limits from Rolimons

## 🔄 Updates

### Backend Updates

1. **Stop service**:
   ```bash
   sudo systemctl stop roblox-trade-engine
   ```

2. **Update code**:
   ```bash
   cd /opt/roblox-trade-engine
   git pull  # or upload new files
   ```

3. **Update dependencies**:
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Restart service**:
   ```bash
   sudo systemctl start roblox-trade-engine
   ```

### GUI Updates

Simply replace the GUI files and restart the application.

---

## 🎯 Quick Start Checklist

- [ ] Server prepared with Python 3.8+
- [ ] Backend code uploaded to server
- [ ] Dependencies installed
- [ ] Backend service running
- [ ] Port 8000 accessible
- [ ] GUI client downloaded locally
- [ ] GUI dependencies installed
- [ ] Backend URL configured in GUI
- [ ] Connection tested successfully
- [ ] Discord webhook configured (optional)
- [ ] First scan completed
- [ ] Results verified

**You're now ready to use the Roblox Trade Command Engine!** 🚀 
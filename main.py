import asyncio
import logging
import time
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config.config_manager import config_manager
from models.data_models import SystemStatus, StrategyMode, ScanResult, MarketMetrics
from scraper.rolimons_scraper import RolimonsScraper
from scoring.score_engine import ScoreEngine
from trade.trade_simulator import TradeSimulator
from discord.discord_handler import DiscordHandler

# Import intelligence modules
from modules.momentum_detector import MomentumDetector
from modules.underpricing_finder import UnderpricingFinder
from modules.calendar_forecaster import CalendarForecaster
from modules.trait_analyzer import TraitAnalyzer
from modules.engagement_miner import EngagementMiner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global variables
start_time = time.time()
last_scan_time = None
scanner_active = False
scraper = None
score_engine = None
trade_simulator = None
discord_handler = None

# Intelligence modules
momentum_detector = None
underpricing_finder = None
calendar_forecaster = None
trait_analyzer = None
engagement_miner = None

# Cache for scan results
cached_items = []
cached_combos = []
cached_market_metrics = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global scraper, score_engine, trade_simulator, discord_handler
    global momentum_detector, underpricing_finder, calendar_forecaster, trait_analyzer, engagement_miner
    
    logger.info("Starting Roblox Trade Command Engine...")
    
    # Initialize components
    try:
        scraper = RolimonsScraper()
        score_engine = ScoreEngine()
        trade_simulator = TradeSimulator()
        discord_handler = DiscordHandler()
        
        # Initialize intelligence modules
        momentum_detector = MomentumDetector()
        underpricing_finder = UnderpricingFinder()
        calendar_forecaster = CalendarForecaster()
        trait_analyzer = TraitAnalyzer()
        engagement_miner = EngagementMiner()
        
        logger.info("All components initialized successfully")
        
        # Send startup notification
        await discord_handler.send_system_alert(
            "🚀 Roblox Trade Command Engine started successfully!",
            "success"
        )
        
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Roblox Trade Command Engine...")
    
    # Send shutdown notification
    if discord_handler:
        await discord_handler.send_system_alert(
            "🛑 Roblox Trade Command Engine shutting down...",
            "warning"
        )
        await discord_handler.close()

# Create FastAPI app
app = FastAPI(
    title="Roblox Trade Command Engine",
    description="Autonomous trading assistant for Roblox Limiteds",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Roblox Trade Command Engine",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/status")
async def get_status():
    """Get system status and health metrics"""
    global start_time, last_scan_time, scanner_active
    
    try:
        return SystemStatus(
            uptime=time.time() - start_time,
            last_scan=last_scan_time,
            current_mode=StrategyMode(config_manager.get_strategy_mode()),
            active_modules=config_manager.get_enabled_modules(),
            cache_size=len(cached_items),
            api_requests_today=0,  # TODO: Implement request tracking
            alerts_sent_today=0,  # TODO: Implement alert tracking
            errors_count=0,  # TODO: Implement error tracking
            is_healthy=True
        )
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scan")
async def run_scan(background_tasks: BackgroundTasks):
    """Run a Rolimons item scan"""
    global last_scan_time, scanner_active
    
    if scanner_active:
        raise HTTPException(status_code=429, detail="Scan already in progress")
    
    try:
        scanner_active = True
        last_scan_time = datetime.now()
        
        # Run scan in background
        background_tasks.add_task(perform_scan)
        
        return {
            "message": "Scan started",
            "timestamp": last_scan_time.isoformat()
        }
    except Exception as e:
        logger.error(f"Error starting scan: {e}")
        scanner_active = False
        raise HTTPException(status_code=500, detail=str(e))

async def perform_scan():
    """Perform the actual market scan"""
    global scanner_active, cached_items, cached_combos, cached_market_metrics
    
    try:
        logger.info("Starting market scan...")
        scan_start_time = time.time()
        
        # 1. Fetch data from Rolimons
        logger.info("Fetching Limited items from Rolimons...")
        items = await scraper.get_limited_items(limit=500)  # Limit for testing
        
        if not items:
            logger.warning("No items fetched from Rolimons")
            return
        
        logger.info(f"Fetched {len(items)} items from Rolimons")
        
        # 2. Run intelligence analysis
        logger.info("Running intelligence analysis...")
        
        # Trait analysis
        items = trait_analyzer.analyze_item_traits(items)
        
        # Engagement analysis
        items = engagement_miner.analyze_social_engagement(items)
        
        # Momentum detection
        momentum_items = momentum_detector.detect_momentum_items(items)
        
        # Undervaluation analysis
        undervalued_items = underpricing_finder.find_undervalued_items(items)
        
        # 3. Score items
        logger.info("Scoring items...")
        scored_items = score_engine.score_items(items)
        
        # 4. Generate trade combos
        logger.info("Generating trade combinations...")
        combos = trade_simulator.get_best_combos(scored_items, limit=10, min_gain=1000)
        
        # 5. Check for Discord alerts
        logger.info("Checking for Discord alerts...")
        alerts_sent = 0
        for combo in combos:
            if await discord_handler.send_trade_alert(combo):
                alerts_sent += 1
        
        # 6. Calculate market metrics
        market_metrics = MarketMetrics(
            total_items=len(items),
            total_value=sum(item.value for item in items),
            average_rap=sum(item.rap for item in items) / len(items) if items else 0,
            market_volatility=sum(item.volatility for item in items) / len(items) if items else 0,
            top_gainers=items[:5],
            top_losers=items[-5:],
            trending_items=momentum_items[:5],
            risk_index=0.5,  # TODO: Implement proper risk calculation
            timestamp=datetime.now()
        )
        
        # 7. Cache results
        cached_items = scored_items
        cached_combos = combos
        cached_market_metrics = market_metrics
        
        scan_duration = time.time() - scan_start_time
        
        # 8. Send summary to Discord
        summary = {
            "items_scanned": len(items),
            "top_picks_count": len(scored_items[:10]),
            "combos_count": len(combos),
            "alerts_sent": alerts_sent,
            "scan_duration": scan_duration
        }
        await discord_handler.send_market_summary(summary)
        
        logger.info(f"Market scan completed in {scan_duration:.2f}s")
        logger.info(f"Found {len(combos)} trade combos, sent {alerts_sent} alerts")
        
    except Exception as e:
        logger.error(f"Error during scan: {e}")
        
        # Send error alert to Discord
        if discord_handler:
            await discord_handler.send_system_alert(
                f"❌ Scan error: {str(e)}",
                "error"
            )
    finally:
        scanner_active = False

@app.get("/top-picks")
async def get_top_picks(limit: int = 10):
    """Return top scored items"""
    try:
        if not cached_items:
            return {
                "top_picks": [],
                "count": 0,
                "timestamp": datetime.now().isoformat(),
                "message": "No scan data available. Run a scan first."
            }
        
        top_picks = cached_items[:limit]
        
        return {
            "top_picks": [
                {
                    "id": item.id,
                    "name": item.name,
                    "value": item.value,
                    "rap": item.rap,
                    "demand": item.demand.value,
                    "volume": item.volume,
                    "momentum_score": item.momentum_score,
                    "trait_score": item.trait_score,
                    "engagement_score": item.engagement_score
                }
                for item in top_picks
            ],
            "count": len(top_picks),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting top picks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/combo")
async def get_best_combos(limit: int = 5):
    """Return best trade combinations"""
    try:
        if not cached_combos:
            return {
                "combos": [],
                "count": 0,
                "timestamp": datetime.now().isoformat(),
                "message": "No scan data available. Run a scan first."
            }
        
        combos = cached_combos[:limit]
        
        return {
            "combos": [
                {
                    "id": combo.id,
                    "items_offered": [item.name for item in combo.items_offered],
                    "items_requested": [item.name for item in combo.items_requested],
                    "projected_gain": combo.projected_gain,
                    "confidence": combo.confidence,
                    "risk_level": combo.risk_level,
                    "strategy_used": combo.strategy_used.value,
                    "roi_percentage": combo.roi_percentage
                }
                for combo in combos
            ],
            "count": len(combos),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting combos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/timeline/{item_id}")
async def get_item_timeline(item_id: int, days: int = 30):
    """Get item's historical data"""
    try:
        # TODO: Implement timeline logic with actual historical data
        return {
            "item_id": item_id,
            "timeline": [],
            "days": days,
            "message": "Timeline feature not yet implemented"
        }
    except Exception as e:
        logger.error(f"Error getting timeline for item {item_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/config")
async def update_config(config_update: dict):
    """Update configuration"""
    try:
        # Update scoring weights
        if "scoring_weights" in config_update:
            from config.config_manager import ScoringWeights
            weights = ScoringWeights(**config_update["scoring_weights"])
            config_manager.update_scoring_weights(weights)
            score_engine.update_weights(weights)
        
        # Update strategy mode
        if "strategy_mode" in config_update:
            mode = config_update["strategy_mode"]
            config_manager.set_strategy_mode(mode)
            score_engine.update_strategy_mode(mode)
        
        # Update Discord config
        if "discord_webhook" in config_update:
            discord_handler.update_config(webhook_url=config_update["discord_webhook"])
        
        if "alert_threshold" in config_update:
            discord_handler.update_config(alert_threshold=config_update["alert_threshold"])
        
        return {"message": "Configuration updated successfully"}
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook")
async def save_webhook(webhook_config: dict):
    """Save Discord webhook configuration"""
    try:
        webhook_url = webhook_config.get("webhook_url")
        role_id = webhook_config.get("role_id")
        alert_threshold = webhook_config.get("alert_threshold", 3500)
        confidence_threshold = webhook_config.get("confidence_threshold", 0.9)
        
        discord_handler.update_config(
            webhook_url=webhook_url,
            role_id=role_id,
            alert_threshold=alert_threshold,
            confidence_threshold=confidence_threshold
        )
        
        # Test the webhook
        if webhook_url:
            test_success = await discord_handler.test_webhook()
            if test_success:
                return {"message": "Webhook configuration saved and tested successfully"}
            else:
                return {"message": "Webhook configuration saved but test failed"}
        
        return {"message": "Webhook configuration saved"}
    except Exception as e:
        logger.error(f"Error saving webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/calendar")
async def get_forecast_calendar():
    """Show forecasted trade windows"""
    try:
        if not cached_items:
            return {
                "forecast_windows": [],
                "timestamp": datetime.now().isoformat(),
                "message": "No scan data available. Run a scan first."
            }
        
        # Get forecast windows
        windows = calendar_forecaster.forecast_trade_windows(cached_items)
        
        return {
            "forecast_windows": [
                {
                    "start_date": window.start_date.isoformat(),
                    "end_date": window.end_date.isoformat(),
                    "confidence": window.confidence,
                    "expected_gain": window.expected_gain,
                    "reasoning": window.reasoning
                }
                for window in windows[:10]  # Limit to top 10
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting calendar: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/risk-index")
async def get_risk_index():
    """Return current market volatility"""
    try:
        if not cached_market_metrics:
            return {
                "risk_index": 0.5,
                "volatility": 0.3,
                "timestamp": datetime.now().isoformat(),
                "message": "No scan data available. Run a scan first."
            }
        
        return {
            "risk_index": cached_market_metrics.risk_index,
            "volatility": cached_market_metrics.market_volatility,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting risk index: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test-discord")
async def test_discord():
    """Test Discord webhook connection"""
    try:
        success = await discord_handler.test_webhook()
        return {
            "success": success,
            "message": "Discord webhook test completed"
        }
    except Exception as e:
        logger.error(f"Error testing Discord: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    # Create logs directory
    import os
    os.makedirs("logs", exist_ok=True)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 
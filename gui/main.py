import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import requests
import json
import time
from datetime import datetime
import webbrowser
from typing import Dict, Any, Optional

class RobloxTradeGUI:
    """Standalone GUI client for Roblox Trade Command Engine"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Roblox Trade Command Engine - Client")
        self.root.geometry("1200x800")
        
        # Backend configuration
        self.backend_url = "http://localhost:8000"  # Default local backend
        self.is_connected = False
        self.scan_running = False
        
        # Data cache
        self.cached_items = []
        self.cached_combos = []
        self.cached_status = {}
        
        # Create GUI
        self.setup_gui()
        
        # Test connection on startup
        self.test_connection()
    
    def setup_gui(self):
        """Setup the main GUI interface"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_trade_console_tab()
        self.create_timeline_tab()
        self.create_strategy_tab()
        self.create_calendar_tab()
        self.create_alerts_tab()
        self.create_debug_tab()
        
        # Status bar
        self.create_status_bar()
    
    def create_dashboard_tab(self):
        """Create the main dashboard tab"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="Dashboard")
        
        # Top controls
        controls_frame = ttk.Frame(dashboard_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Backend URL
        ttk.Label(controls_frame, text="Backend URL:").pack(side=tk.LEFT)
        self.url_entry = ttk.Entry(controls_frame, width=30)
        self.url_entry.pack(side=tk.LEFT, padx=5)
        self.url_entry.insert(0, self.backend_url)
        
        # Connect button
        self.connect_btn = ttk.Button(controls_frame, text="Connect", command=self.test_connection)
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
        # Scan button
        self.scan_btn = ttk.Button(controls_frame, text="Start Scan", command=self.start_scan)
        self.scan_btn.pack(side=tk.LEFT, padx=5)
        
        # Status indicator
        self.status_label = ttk.Label(controls_frame, text="Disconnected", foreground="red")
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Main content area
        content_frame = ttk.Frame(dashboard_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel - Top picks
        left_frame = ttk.LabelFrame(content_frame, text="Top Picks")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Top picks treeview
        columns = ("Name", "Value", "RAP", "Demand", "Score")
        self.top_picks_tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.top_picks_tree.heading(col, text=col)
            self.top_picks_tree.column(col, width=100)
        
        self.top_picks_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Right panel - System status
        right_frame = ttk.LabelFrame(content_frame, text="System Status")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Status text
        self.status_text = scrolledtext.ScrolledText(right_frame, height=20, width=40)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Refresh button
        refresh_btn = ttk.Button(right_frame, text="Refresh Status", command=self.refresh_status)
        refresh_btn.pack(pady=5)
    
    def create_trade_console_tab(self):
        """Create the trade console tab"""
        console_frame = ttk.Frame(self.notebook)
        self.notebook.add(console_frame, text="Trade Console")
        
        # Trade combos
        combos_frame = ttk.LabelFrame(console_frame, text="Best Trade Combinations")
        combos_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Combos treeview
        columns = ("Offered", "Requested", "Gain", "Confidence", "Risk")
        self.combos_tree = ttk.Treeview(combos_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.combos_tree.heading(col, text=col)
            self.combos_tree.column(col, width=150)
        
        self.combos_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Combo details
        details_frame = ttk.LabelFrame(console_frame, text="Combo Details")
        details_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.combo_details = scrolledtext.ScrolledText(details_frame, height=8)
        self.combo_details.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bind selection event
        self.combos_tree.bind("<<TreeviewSelect>>", self.on_combo_select)
    
    def create_timeline_tab(self):
        """Create the timeline viewer tab"""
        timeline_frame = ttk.Frame(self.notebook)
        self.notebook.add(timeline_frame, text="Timeline")
        
        # Item selection
        select_frame = ttk.Frame(timeline_frame)
        select_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(select_frame, text="Item ID:").pack(side=tk.LEFT)
        self.item_id_entry = ttk.Entry(select_frame, width=10)
        self.item_id_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(select_frame, text="Days:").pack(side=tk.LEFT, padx=(10, 0))
        self.days_entry = ttk.Entry(select_frame, width=5)
        self.days_entry.pack(side=tk.LEFT, padx=5)
        self.days_entry.insert(0, "30")
        
        load_btn = ttk.Button(select_frame, text="Load Timeline", command=self.load_timeline)
        load_btn.pack(side=tk.LEFT, padx=10)
        
        # Timeline display
        timeline_display_frame = ttk.LabelFrame(timeline_frame, text="Price Timeline")
        timeline_display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.timeline_text = scrolledtext.ScrolledText(timeline_display_frame)
        self.timeline_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_strategy_tab(self):
        """Create the strategy configuration tab"""
        strategy_frame = ttk.Frame(self.notebook)
        self.notebook.add(strategy_frame, text="Strategy Config")
        
        # Strategy mode
        mode_frame = ttk.LabelFrame(strategy_frame, text="Strategy Mode")
        mode_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.strategy_var = tk.StringVar(value="conservative")
        strategies = [
            ("Conservative", "conservative"),
            ("Aggressive", "aggressive"),
            ("Sniper", "sniper"),
            ("Momentum", "momentum")
        ]
        
        for text, value in strategies:
            ttk.Radiobutton(mode_frame, text=text, variable=self.strategy_var, 
                          value=value, command=self.update_strategy).pack(anchor=tk.W, padx=10, pady=2)
        
        # Scoring weights
        weights_frame = ttk.LabelFrame(strategy_frame, text="Scoring Weights")
        weights_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create weight sliders
        self.weight_vars = {}
        weights = [
            ("ROI Weight", "roi_weight", 0.3),
            ("Demand Weight", "demand_weight", 0.2),
            ("Volume Weight", "volume_weight", 0.15),
            ("Volatility Weight", "volatility_weight", 0.1),
            ("Engagement Weight", "engagement_weight", 0.15),
            ("Trait Weight", "trait_weight", 0.1)
        ]
        
        for label, key, default in weights:
            frame = ttk.Frame(weights_frame)
            frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(frame, text=label).pack(side=tk.LEFT)
            
            var = tk.DoubleVar(value=default)
            self.weight_vars[key] = var
            
            slider = ttk.Scale(frame, from_=0, to=1, variable=var, orient=tk.HORIZONTAL)
            slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
            
            value_label = ttk.Label(frame, text=f"{default:.2f}")
            value_label.pack(side=tk.RIGHT)
            
            # Update label when slider changes
            slider.configure(command=lambda val, lbl=value_label: lbl.configure(text=f"{float(val):.2f}"))
        
        # Save button
        save_btn = ttk.Button(strategy_frame, text="Save Configuration", command=self.save_config)
        save_btn.pack(pady=10)
    
    def create_calendar_tab(self):
        """Create the calendar tab"""
        calendar_frame = ttk.Frame(self.notebook)
        self.notebook.add(calendar_frame, text="Calendar")
        
        # Calendar display
        calendar_display_frame = ttk.LabelFrame(calendar_frame, text="Forecasted Trade Windows")
        calendar_display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Calendar treeview
        columns = ("Start Date", "End Date", "Confidence", "Expected Gain", "Reasoning")
        self.calendar_tree = ttk.Treeview(calendar_display_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.calendar_tree.heading(col, text=col)
            self.calendar_tree.column(col, width=150)
        
        self.calendar_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Refresh button
        refresh_calendar_btn = ttk.Button(calendar_frame, text="Refresh Calendar", command=self.load_calendar)
        refresh_calendar_btn.pack(pady=5)
    
    def create_alerts_tab(self):
        """Create the alerts log tab"""
        alerts_frame = ttk.Frame(self.notebook)
        self.notebook.add(alerts_frame, text="Alerts")
        
        # Discord webhook configuration
        webhook_frame = ttk.LabelFrame(alerts_frame, text="Discord Webhook Configuration")
        webhook_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Webhook URL
        url_frame = ttk.Frame(webhook_frame)
        url_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(url_frame, text="Webhook URL:").pack(side=tk.LEFT)
        self.webhook_url_entry = ttk.Entry(url_frame, width=50)
        self.webhook_url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Role ID
        role_frame = ttk.Frame(webhook_frame)
        role_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(role_frame, text="Role ID:").pack(side=tk.LEFT)
        self.role_id_entry = ttk.Entry(role_frame, width=20)
        self.role_id_entry.pack(side=tk.LEFT, padx=5)
        
        # Alert threshold
        threshold_frame = ttk.Frame(webhook_frame)
        threshold_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(threshold_frame, text="Alert Threshold (Robux):").pack(side=tk.LEFT)
        self.threshold_entry = ttk.Entry(threshold_frame, width=10)
        self.threshold_entry.pack(side=tk.LEFT, padx=5)
        self.threshold_entry.insert(0, "3500")
        
        # Buttons
        button_frame = ttk.Frame(webhook_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        save_webhook_btn = ttk.Button(button_frame, text="Save Webhook", command=self.save_webhook)
        save_webhook_btn.pack(side=tk.LEFT, padx=5)
        
        test_webhook_btn = ttk.Button(button_frame, text="Test Webhook", command=self.test_webhook)
        test_webhook_btn.pack(side=tk.LEFT, padx=5)
        
        # Alert log
        log_frame = ttk.LabelFrame(alerts_frame, text="Alert Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.alert_log = scrolledtext.ScrolledText(log_frame, height=15)
        self.alert_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_debug_tab(self):
        """Create the debug tab"""
        debug_frame = ttk.Frame(self.notebook)
        self.notebook.add(debug_frame, text="Debug")
        
        # Endpoint testing
        endpoint_frame = ttk.LabelFrame(debug_frame, text="API Endpoint Testing")
        endpoint_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Endpoint list
        endpoints_frame = ttk.Frame(endpoint_frame)
        endpoints_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(endpoints_frame, text="Endpoint:").pack(side=tk.LEFT)
        self.endpoint_var = tk.StringVar()
        endpoint_combo = ttk.Combobox(endpoints_frame, textvariable=self.endpoint_var, width=30)
        endpoint_combo['values'] = [
            "GET /",
            "GET /status",
            "GET /scan",
            "GET /top-picks",
            "GET /combo",
            "GET /calendar",
            "GET /risk-index",
            "GET /test-discord",
            "POST /config",
            "POST /webhook"
        ]
        endpoint_combo.pack(side=tk.LEFT, padx=5)
        endpoint_combo.set("GET /status")
        
        # Test button
        test_endpoint_btn = ttk.Button(endpoints_frame, text="Test Endpoint", command=self.test_endpoint)
        test_endpoint_btn.pack(side=tk.LEFT, padx=10)
        
        # Response display
        response_frame = ttk.LabelFrame(endpoint_frame, text="Response")
        response_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.response_text = scrolledtext.ScrolledText(response_frame, height=20)
        self.response_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Performance metrics
        metrics_frame = ttk.LabelFrame(debug_frame, text="Performance Metrics")
        metrics_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.metrics_text = scrolledtext.ScrolledText(metrics_frame, height=8)
        self.metrics_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_status_bar(self):
        """Create the status bar"""
        status_bar = ttk.Frame(self.root)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_bar_label = ttk.Label(status_bar, text="Ready")
        self.status_bar_label.pack(side=tk.LEFT, padx=5)
        
        # Auto-refresh checkbox
        self.auto_refresh_var = tk.BooleanVar(value=True)
        auto_refresh_cb = ttk.Checkbutton(status_bar, text="Auto-refresh", variable=self.auto_refresh_var)
        auto_refresh_cb.pack(side=tk.RIGHT, padx=5)
    
    def test_connection(self):
        """Test connection to backend"""
        try:
            self.backend_url = self.url_entry.get()
            response = requests.get(f"{self.backend_url}/", timeout=5)
            
            if response.status_code == 200:
                self.is_connected = True
                self.status_label.configure(text="Connected", foreground="green")
                self.connect_btn.configure(text="Reconnect")
                self.status_bar_label.configure(text="Connected to backend")
                
                # Load initial data
                self.refresh_status()
                self.load_top_picks()
                self.load_combos()
                
                messagebox.showinfo("Success", "Connected to backend successfully!")
            else:
                raise Exception(f"HTTP {response.status_code}")
                
        except Exception as e:
            self.is_connected = False
            self.status_label.configure(text="Disconnected", foreground="red")
            self.connect_btn.configure(text="Connect")
            self.status_bar_label.configure(text="Connection failed")
            messagebox.showerror("Connection Error", f"Failed to connect to backend: {str(e)}")
    
    def start_scan(self):
        """Start a market scan"""
        if not self.is_connected:
            messagebox.showerror("Error", "Not connected to backend")
            return
        
        if self.scan_running:
            messagebox.showwarning("Warning", "Scan already in progress")
            return
        
        try:
            self.scan_running = True
            self.scan_btn.configure(text="Scanning...", state="disabled")
            self.status_bar_label.configure(text="Starting scan...")
            
            # Start scan in background thread
            thread = threading.Thread(target=self._run_scan)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.scan_running = False
            self.scan_btn.configure(text="Start Scan", state="normal")
            messagebox.showerror("Error", f"Failed to start scan: {str(e)}")
    
    def _run_scan(self):
        """Run the scan in background thread"""
        try:
            response = requests.get(f"{self.backend_url}/scan", timeout=30)
            
            if response.status_code == 200:
                # Poll for completion
                while True:
                    time.sleep(2)
                    status_response = requests.get(f"{self.backend_url}/status")
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        if not status_data.get("scanner_active", False):
                            break
                
                # Refresh data
                self.root.after(0, self._scan_completed)
            else:
                raise Exception(f"HTTP {response.status_code}")
                
        except Exception as e:
            self.root.after(0, lambda: self._scan_failed(str(e)))
    
    def _scan_completed(self):
        """Handle scan completion"""
        self.scan_running = False
        self.scan_btn.configure(text="Start Scan", state="normal")
        self.status_bar_label.configure(text="Scan completed")
        
        # Refresh data
        self.refresh_status()
        self.load_top_picks()
        self.load_combos()
        self.load_calendar()
        
        messagebox.showinfo("Success", "Market scan completed!")
    
    def _scan_failed(self, error):
        """Handle scan failure"""
        self.scan_running = False
        self.scan_btn.configure(text="Start Scan", state="normal")
        self.status_bar_label.configure(text="Scan failed")
        messagebox.showerror("Error", f"Scan failed: {error}")
    
    def refresh_status(self):
        """Refresh system status"""
        if not self.is_connected:
            return
        
        try:
            response = requests.get(f"{self.backend_url}/status", timeout=5)
            if response.status_code == 200:
                status_data = response.json()
                self.cached_status = status_data
                
                # Update status display
                status_text = f"System Status:\n"
                status_text += f"Uptime: {status_data.get('uptime', 0):.1f}s\n"
                status_text += f"Mode: {status_data.get('current_mode', 'Unknown')}\n"
                status_text += f"Cache Size: {status_data.get('cache_size', 0)} items\n"
                status_text += f"Last Scan: {status_data.get('last_scan', 'Never')}\n"
                status_text += f"Active Modules: {', '.join(status_data.get('active_modules', []))}\n"
                
                self.status_text.delete(1.0, tk.END)
                self.status_text.insert(1.0, status_text)
                
        except Exception as e:
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(1.0, f"Error loading status: {str(e)}")
    
    def load_top_picks(self):
        """Load top picks data"""
        if not self.is_connected:
            return
        
        try:
            response = requests.get(f"{self.backend_url}/top-picks", timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                # Clear existing items
                for item in self.top_picks_tree.get_children():
                    self.top_picks_tree.delete(item)
                
                # Add new items
                for item in data.get("top_picks", []):
                    self.top_picks_tree.insert("", tk.END, values=(
                        item.get("name", ""),
                        f"{item.get('value', 0):,}",
                        f"{item.get('rap', 0):,}",
                        item.get("demand", ""),
                        f"{item.get('momentum_score', 0):.2f}"
                    ))
                
                self.cached_items = data.get("top_picks", [])
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load top picks: {str(e)}")
    
    def load_combos(self):
        """Load trade combinations"""
        if not self.is_connected:
            return
        
        try:
            response = requests.get(f"{self.backend_url}/combo", timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                # Clear existing items
                for item in self.combos_tree.get_children():
                    self.combos_tree.delete(item)
                
                # Add new items
                for combo in data.get("combos", []):
                    self.combos_tree.insert("", tk.END, values=(
                        " + ".join(combo.get("items_offered", [])),
                        " + ".join(combo.get("items_requested", [])),
                        f"{combo.get('projected_gain', 0):,}",
                        f"{combo.get('confidence', 0):.1%}",
                        combo.get("risk_level", "")
                    ))
                
                self.cached_combos = data.get("combos", [])
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load combos: {str(e)}")
    
    def on_combo_select(self, event):
        """Handle combo selection"""
        selection = self.combos_tree.selection()
        if not selection:
            return
        
        # Get selected combo index
        item = self.combos_tree.item(selection[0])
        index = self.combos_tree.index(selection[0])
        
        if index < len(self.cached_combos):
            combo = self.cached_combos[index]
            
            details = f"Combo Details:\n\n"
            details += f"Items Offered: {' + '.join(combo.get('items_offered', []))}\n"
            details += f"Items Requested: {' + '.join(combo.get('items_requested', []))}\n"
            details += f"Projected Gain: {combo.get('projected_gain', 0):,} Robux\n"
            details += f"Confidence: {combo.get('confidence', 0):.1%}\n"
            details += f"Risk Level: {combo.get('risk_level', '')}\n"
            details += f"Strategy: {combo.get('strategy_used', '')}\n"
            details += f"ROI: {combo.get('roi_percentage', 0):.1%}\n"
            
            self.combo_details.delete(1.0, tk.END)
            self.combo_details.insert(1.0, details)
    
    def load_timeline(self):
        """Load item timeline"""
        if not self.is_connected:
            return
        
        try:
            item_id = self.item_id_entry.get()
            days = self.days_entry.get()
            
            if not item_id:
                messagebox.showwarning("Warning", "Please enter an item ID")
                return
            
            response = requests.get(f"{self.backend_url}/timeline/{item_id}?days={days}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                self.timeline_text.delete(1.0, tk.END)
                self.timeline_text.insert(1.0, json.dumps(data, indent=2))
            else:
                raise Exception(f"HTTP {response.status_code}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load timeline: {str(e)}")
    
    def load_calendar(self):
        """Load forecast calendar"""
        if not self.is_connected:
            return
        
        try:
            response = requests.get(f"{self.backend_url}/calendar", timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                # Clear existing items
                for item in self.calendar_tree.get_children():
                    self.calendar_tree.delete(item)
                
                # Add new items
                for window in data.get("forecast_windows", []):
                    self.calendar_tree.insert("", tk.END, values=(
                        window.get("start_date", ""),
                        window.get("end_date", ""),
                        f"{window.get('confidence', 0):.1%}",
                        f"{window.get('expected_gain', 0):,}",
                        window.get("reasoning", "")
                    ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load calendar: {str(e)}")
    
    def update_strategy(self):
        """Update strategy mode"""
        if not self.is_connected:
            return
        
        try:
            strategy = self.strategy_var.get()
            config_data = {"strategy_mode": strategy}
            
            response = requests.post(f"{self.backend_url}/config", json=config_data, timeout=5)
            if response.status_code == 200:
                messagebox.showinfo("Success", f"Strategy updated to {strategy.title()}")
            else:
                raise Exception(f"HTTP {response.status_code}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update strategy: {str(e)}")
    
    def save_config(self):
        """Save configuration"""
        if not self.is_connected:
            return
        
        try:
            # Build weights config
            weights = {}
            for key, var in self.weight_vars.items():
                weights[key] = var.get()
            
            config_data = {
                "scoring_weights": weights
            }
            
            response = requests.post(f"{self.backend_url}/config", json=config_data, timeout=5)
            if response.status_code == 200:
                messagebox.showinfo("Success", "Configuration saved successfully")
            else:
                raise Exception(f"HTTP {response.status_code}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
    
    def save_webhook(self):
        """Save Discord webhook configuration"""
        if not self.is_connected:
            return
        
        try:
            webhook_data = {
                "webhook_url": self.webhook_url_entry.get(),
                "role_id": self.role_id_entry.get(),
                "alert_threshold": int(self.threshold_entry.get())
            }
            
            response = requests.post(f"{self.backend_url}/webhook", json=webhook_data, timeout=5)
            if response.status_code == 200:
                data = response.json()
                messagebox.showinfo("Success", data.get("message", "Webhook saved"))
            else:
                raise Exception(f"HTTP {response.status_code}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save webhook: {str(e)}")
    
    def test_webhook(self):
        """Test Discord webhook"""
        if not self.is_connected:
            return
        
        try:
            response = requests.get(f"{self.backend_url}/test-discord", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    messagebox.showinfo("Success", "Discord webhook test successful!")
                else:
                    messagebox.showwarning("Warning", "Discord webhook test failed")
            else:
                raise Exception(f"HTTP {response.status_code}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to test webhook: {str(e)}")
    
    def test_endpoint(self):
        """Test API endpoint"""
        if not self.is_connected:
            return
        
        try:
            endpoint = self.endpoint_var.get()
            if not endpoint:
                messagebox.showwarning("Warning", "Please select an endpoint")
                return
            
            method, path = endpoint.split(" ", 1)
            
            if method == "GET":
                response = requests.get(f"{self.backend_url}{path}", timeout=10)
            elif method == "POST":
                response = requests.post(f"{self.backend_url}{path}", json={}, timeout=10)
            else:
                raise Exception(f"Unsupported method: {method}")
            
            # Display response
            self.response_text.delete(1.0, tk.END)
            self.response_text.insert(1.0, f"Status: {response.status_code}\n\n")
            self.response_text.insert(tk.END, json.dumps(response.json(), indent=2))
            
            # Update metrics
            self.metrics_text.delete(1.0, tk.END)
            self.metrics_text.insert(1.0, f"Response Time: {response.elapsed.total_seconds():.3f}s\n")
            self.metrics_text.insert(tk.END, f"Content Length: {len(response.content)} bytes\n")
            
        except Exception as e:
            self.response_text.delete(1.0, tk.END)
            self.response_text.insert(1.0, f"Error: {str(e)}")

def main():
    """Main function"""
    root = tk.Tk()
    app = RobloxTradeGUI(root)
    
    # Start auto-refresh timer
    def auto_refresh():
        if app.auto_refresh_var.get() and app.is_connected:
            app.refresh_status()
        root.after(30000, auto_refresh)  # Refresh every 30 seconds
    
    root.after(30000, auto_refresh)
    
    root.mainloop()

if __name__ == "__main__":
    main() 
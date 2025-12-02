# Quick Start Guide - New Relic Flask Demo App

## 📥 Getting Started (5 minutes)

### Step 1: Clone the Repository
```bash
git clone https://github.com/aakashb87/nr-sample-app.git
cd nr-sample-app
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Set Up Database (Optional)
If you want to use the database features:
```bash
python init_db.py
```

---

## 🚀 Running the App

### Start the Flask Application
```bash
python app.py
```

The app will start on **http://localhost:5000**

**Available Endpoints:**
- http://localhost:5000/ - Hello World
- http://localhost:5000/about - About page
- http://localhost:5000/status - App status
- http://localhost:5000/products - List all products
- http://localhost:5000/products/slow - Slow query (for testing)
- http://localhost:5000/cpu-heavy - CPU-intensive endpoint
- http://localhost:5000/file-large - Large response
- http://localhost:5000/db-health - Database health check
- http://localhost:5000/metrics - Prometheus metrics
- http://localhost:5000/routes - List all routes

---

## 🔄 Auto-Refresh All Pages (Optional)

Want to continuously load all endpoints for monitoring/testing?

### Step 1: Install Selenium
```bash
pip install selenium
```

### Step 2: Start the Flask App (in one terminal)
```bash
python app.py
```

### Step 3: Run Auto-Refresh Script (in another terminal)
```bash
python auto_refresh_pages.py
```

**What it does:**
- Opens all 9 endpoints in separate browser tabs
- Automatically refreshes them every 30 seconds
- Great for continuous monitoring and generating metrics
- Press `Ctrl+C` to stop

---

## 📊 Monitoring Features

This app includes:

### ✅ New Relic APM
- Automatic instrumentation
- Transaction tracing
- Performance monitoring

### ✅ OpenTelemetry
- Distributed tracing sent to New Relic
- Flask and PostgreSQL instrumentation

### ✅ Prometheus Metrics
- Available at `/metrics` endpoint
- Custom metrics for database health
- Request duration and counts

---

## ⚙️ Configuration

### Database Connection
Edit these environment variables or update `app.py`:
```python
PG_HOST = "your-database-host"
PG_DB = "your-database-name"
PG_USER = "your-username"
PG_PASSWORD = "your-password"
```

### New Relic Configuration
Edit `newrelic.ini`:
```ini
license_key = YOUR_LICENSE_KEY
app_name = Your App Name
```

---

## 🎯 Typical Workflow

### For Demo/Testing:
```bash
# 1. Clone and setup
git clone https://github.com/aakashb87/nr-sample-app.git
cd nr-sample-app
pip install -r requirements.txt

# 2. Start the app
python app.py

# 3. Open browser to http://localhost:5000
# Or run auto-refresh script in another terminal:
python auto_refresh_pages.py
```

### For Azure Deployment:
This app is ready to deploy to Azure App Service. See the main README.md for Azure deployment instructions.

---

## 🧪 Testing Endpoints

### Test Normal Performance
```bash
curl http://localhost:5000/products
```

### Test Slow Query (for monitoring alerts)
```bash
curl http://localhost:5000/products/slow
```

### Test CPU Load
```bash
curl http://localhost:5000/cpu-heavy
```

### Check Database Health
```bash
curl http://localhost:5000/db-health
```

### View Prometheus Metrics
```bash
curl http://localhost:5000/metrics
```

---

## ❓ Troubleshooting

**Problem**: Database connection error  
**Solution**: Update database credentials in `app.py` or set environment variables

**Problem**: Port 5000 already in use  
**Solution**: Change port in `app.py`: `app.run(port=5001)`

**Problem**: Selenium/ChromeDriver error  
**Solution**: 
1. Make sure Chrome browser is installed
2. ChromeDriver will be installed automatically with `pip install selenium`

**Problem**: Module not found errors  
**Solution**: Run `pip install -r requirements.txt`

---

## 📁 Project Files

```
nr-sample-app/
├── app.py                      # Main Flask application
├── app1.py                     # Alternative app version
├── auto_refresh_pages.py       # Auto-refresh script
├── init_db.py                  # Database initialization
├── newrelic.ini               # New Relic configuration
├── requirements.txt           # Python dependencies
└── README.md                  # Full documentation
```

---

## 🎓 Use Cases

- **Local Development**: Test monitoring integration locally
- **Demo/Presentation**: Show real-time monitoring with auto-refresh
- **Load Testing**: Generate continuous traffic for testing alerts
- **Azure Deployment**: Ready-to-deploy Flask app for Azure App Service

---

## 🔑 Key Features

- ✅ Multiple monitoring solutions integrated (New Relic, OpenTelemetry, Prometheus)
- ✅ Realistic endpoints for testing different scenarios
- ✅ Database health checks with metrics
- ✅ Auto-refresh tool for continuous monitoring
- ✅ Production-ready with proper error handling

---

**That's it!** Just clone, install dependencies, and run. The app is designed to work out of the box.

**Note**: For production use, make sure to update the database credentials and New Relic license key in the configuration files.

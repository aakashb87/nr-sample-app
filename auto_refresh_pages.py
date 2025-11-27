"""
Auto-refresh script for Flask app endpoints.
Opens all app endpoints in browser tabs and refreshes them every 30 seconds.
Uses Selenium WebDriver to control the browser and refresh existing tabs.
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
import time
from datetime import datetime

# Base URL for the Flask app
BASE_URL = "http://localhost:5000"

# All endpoints from the Flask app
ENDPOINTS = [
    "/",
    "/about",
    "/status",
    "/products",
    "/products/slow",
    "/cpu-heavy",
    "/file-large",
    "/db-health",
    "/routes",
]

def setup_driver():
    """Setup Chrome WebDriver with appropriate options."""
    chrome_options = Options()
    # Remove headless mode so you can see the browser
    # chrome_options.add_argument('--headless')  
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except WebDriverException as e:
        print("Error: Chrome WebDriver not found.")
        print("Please install it using: pip install selenium")
        print("And download ChromeDriver from: https://chromedriver.chromium.org/")
        raise

def open_all_tabs(driver):
    """Open all endpoints in separate browser tabs."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Opening all pages in browser tabs...")
    
    # Open first URL in the main window
    url = BASE_URL + ENDPOINTS[0]
    print(f"  Tab 1: {url}")
    driver.get(url)
    time.sleep(0.5)
    
    # Open remaining URLs in new tabs
    for i, endpoint in enumerate(ENDPOINTS[1:], start=2):
        url = BASE_URL + endpoint
        print(f"  Tab {i}: {url}")
        driver.execute_script(f"window.open('{url}', '_blank');")
        time.sleep(0.5)
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] All {len(ENDPOINTS)} tabs opened.")

def refresh_all_tabs(driver):
    """Refresh all open tabs by switching to each and calling refresh."""
    original_window = driver.current_window_handle
    all_windows = driver.window_handles
    
    for i, window in enumerate(all_windows, start=1):
        driver.switch_to.window(window)
        current_url = driver.current_url
        print(f"  Tab {i}: Refreshing {current_url}")
        driver.refresh()
        time.sleep(0.3)
    
    # Switch back to the first tab
    driver.switch_to.window(original_window)

def refresh_cycle():
    """Main function to continuously refresh all pages every 30 seconds."""
    print(f"\n{'='*60}")
    print("Auto-Refresh Script Started (Selenium)")
    print(f"{'='*60}")
    print(f"Base URL: {BASE_URL}")
    print(f"Refresh Interval: 30 seconds")
    print(f"Endpoints to monitor: {len(ENDPOINTS)}")
    print(f"{'='*60}\n")
    
    print("Initializing Chrome WebDriver...")
    driver = setup_driver()
    
    try:
        # Open all pages initially
        open_all_tabs(driver)
        
        print(f"\nPages will refresh every 30 seconds.")
        print("Press Ctrl+C to stop.\n")
        
        cycle = 1
        while True:
            time.sleep(30)  # Wait 30 seconds
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Refresh cycle #{cycle}")
            print("-" * 60)
            
            refresh_all_tabs(driver)
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] All {len(ENDPOINTS)} tabs refreshed.")
            cycle += 1
            
    except KeyboardInterrupt:
        print(f"\n\n[{datetime.now().strftime('%H:%M:%S')}] Auto-refresh stopped by user.")
        print(f"Total refresh cycles completed: {cycle - 1}")
    
    finally:
        print("Closing browser...")
        driver.quit()
        print("Browser closed.")

if __name__ == "__main__":
    print("\nMake sure your Flask app is running on http://localhost:5000")
    print("Starting in 3 seconds...\n")
    time.sleep(3)
    refresh_cycle()

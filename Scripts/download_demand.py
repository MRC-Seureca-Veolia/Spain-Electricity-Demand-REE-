import os
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# === CONFIGURATION ===
download_dir = os.path.join(os.path.dirname(__file__), "../Daily Demand")
os.makedirs(download_dir, exist_ok=True)

# === HEADLESS CHROME CONFIG ===
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.binary_location = "/usr/bin/chromium-browser"
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": os.path.abspath(download_dir),
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "safebrowsing.enabled": True
})

driver = webdriver.Chrome(options=chrome_options)

# === DYNAMIC DATE ===
yesterday = datetime.utcnow() - timedelta(days=1)
start_str = yesterday.strftime("%d-%m-%Y")

url = f"https://www.esios.ree.es/es/analisis/1293?vis=1&start_date={start_str}T00%3A00&end_date={start_str}T23%3A55&groupby=hour"
driver.get(url)

try:
    print("⏳ Waiting for export button...")

    # Accept cookies
    try:
        cookie_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Aceptar')]"))
        )
        cookie_button.click()
        print("🍪 Cookies accepted")
    except:
        print("🍪 No cookie popup")

    # Click EXPORTACIÓN
    export_button = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.ID, "export_multiple"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", export_button)
    time.sleep(1)
    export_button.click()

    # Click CSV
    csv_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@class='opt-ancle' and contains(text(), 'CSV')]"))
    )
    driver.execute_script("arguments[0].click();", csv_option)
    print("📄 CSV clicked, downloading...")

    # Wait for download (simple wait)
    time.sleep(10)

except Exception as e:
    print("❌ Error:", e)

driver.quit()
print(f"✅ Done. Check here:\n📁 {os.path.abspath(download_dir)}")


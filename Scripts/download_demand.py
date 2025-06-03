import os
import time
import tempfile
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# === CREATE DYNAMIC DOWNLOAD FOLDER ===
download_dir = os.path.join(os.getcwd(), "Daily-Demand")
os.makedirs(download_dir, exist_ok=True)

# === SETUP HEADLESS CHROME ===
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920,1080")

# Fix for GitHub Actions: use isolated user data dir
tmp_user_data_dir = tempfile.mkdtemp()
chrome_options.add_argument(f"--user-data-dir={tmp_user_data_dir}")

chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "safebrowsing.enabled": True
})

# Set up driver explicitly using the known path
driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=chrome_options)

# === BUILD URL ===
yesterday = datetime.utcnow() - timedelta(days=1)
date_str = yesterday.strftime("%d-%m-%Y")
url = f"https://www.esios.ree.es/es/analisis/1293?vis=1&start_date={date_str}T00%3A00&end_date={date_str}T23%3A55&groupby=hour"

driver.get(url)

try:
    print("⏳ Waiting for export button...")

    # Accept cookies if any
    try:
        cookie_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Aceptar')]"))
        )
        cookie_button.click()
        print("🍪 Cookies accepted")
    except:
        print("🍪 No cookie popup")

    # Export CSV
    export_button = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.ID, "export_multiple"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", export_button)
    time.sleep(1)
    export_button.click()

    csv_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@class='opt-ancle' and contains(text(), 'CSV')]"))
    )
    driver.execute_script("arguments[0].click();", csv_option)

    print("📄 CSV clicked, downloading...")
    time.sleep(10)  # wait for download to complete

except Exception as e:
    print("❌ Error:", e)

driver.quit()
print(f"✅ Done. Check folder:\n📁 {download_dir}")


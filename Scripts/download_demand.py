import os
import time
import glob
import shutil
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# === Set download directory ===
download_dir = os.path.join(os.getcwd(), "Daily-Demand")
os.makedirs(download_dir, exist_ok=True)

# === Headless Chromium config ===
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.binary_location = "/snap/bin/chromium"  # 👈 important fix

chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "safebrowsing.enabled": True
})

# Explicitly define chromedriver path (installed via apt)
driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=chrome_options)

# === Calculate yesterday ===
yesterday = datetime.utcnow() - timedelta(days=1)
date_str = yesterday.strftime("%d-%m-%Y")

# === Open ESIOS URL ===
url = f"https://www.esios.ree.es/es/analisis/1293?vis=1&start_date={date_str}T00%3A00&end_date={date_str}T23%3A55&groupby=hour"
driver.get(url)

try:
    print("⏳ Waiting for export button...")

    # Accept cookie popup if appears
    try:
        cookie_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Aceptar')]"))
        )
        cookie_button.click()
        print("🍪 Cookies accepted")
    except:
        print("🍪 No cookie popup")

    # Click export button
    export_button = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.ID, "export_multiple"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", export_button)
    time.sleep(1)
    export_button.click()

    # Click CSV option
    csv_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@class='opt-ancle' and contains(text(), 'CSV')]"))
    )
    driver.execute_script("arguments[0].click();", csv_option)
    print("📄 CSV clicked, downloading...")

    time.sleep(10)

    # Check if file exists
    downloaded_files = glob.glob(os.path.join(download_dir, "*.csv"))
    if downloaded_files:
        print("✅ CSV file saved in:", download_dir)
    else:
        print("⚠️ No CSV file found.")

except Exception as e:
    print("❌ Error:", e)

finally:
    driver.quit()
    print("✅ Done.")

import os
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# === CONFIGURATION ===
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
download_dir = os.path.join(base_dir, "Daily-Demand")
os.makedirs(download_dir, exist_ok=True)

# Calculate yesterday's date
yesterday = datetime.today() - timedelta(days=1)
date_str = yesterday.strftime("%d-%m-%Y")
iso_str = yesterday.strftime("%Y-%m-%d")

# Dynamic URL
url = f"https://www.esios.ree.es/es/analisis/1293?vis=1&start_date={date_str}T00%3A00&end_date={date_str}T23%3A55&groupby=hour"

# === HEADLESS CHROME CONFIG ===
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "safebrowsing.enabled": True
})

driver = webdriver.Chrome(options=chrome_options)

# === SCRAPING ===
driver.get(url)

try:
    print("⏳ Waiting for export button...")

    # Accept cookies if shown
    try:
        cookie_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Aceptar')]"))
        )
        cookie_button.click()
        print("🍪 Cookies accepted")
    except:
        print("🍪 No cookie popup")

    # Click export
    export_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, "export_multiple"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", export_button)
    export_button.click()

    # Click CSV
    csv_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'opt-ancle') and contains(text(),'CSV')]"))
    )
    driver.execute_script("arguments[0].click();", csv_option)
    print("📄 CSV clicked, downloading...")

    # Wait for file to appear
    def wait_for_download(directory, timeout=30):
        end_time = time.time() + timeout
        while time.time() < end_time:
            for file in os.listdir(directory):
                if file.endswith(".csv") or file.endswith(".xls"):
                    return os.path.join(directory, file)
            time.sleep(1)
        return None

    downloaded_file = wait_for_download(download_dir)

    if downloaded_file:
        new_filename = os.path.join(download_dir, f"{iso_str}.csv")
        os.rename(downloaded_file, new_filename)
        print(f"✅ File saved as: {new_filename}")
    else:
        print("❌ Download failed or timed out.")

except Exception as e:
    print("❌ Error:", e)

finally:
    driver.quit()
    print("✅ Done.")

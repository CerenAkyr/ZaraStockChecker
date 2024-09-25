import json
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from playsound import playsound
from scraperHelpers import check_stock, rossmannStockCheck

# Load configuration from config.json
with open("config.json", "r") as config_file:
    config = json.load(config_file)

# Extract configuration values
urls_to_check = config["urls"]
sizes_to_check = config["sizes_to_check"]
sleep_min_seconds = config["sleep_min_seconds"]
sleep_max_seconds = config["sleep_max_seconds"]
chrome_driver_path = config["chrome_driver_path"]

# To only add to the cart once :)
cart_status = {item["url"]: False for item in urls_to_check}


while True:
    # Create a service object with the path to ChromeDriver from the config
    service = Service(executable_path=chrome_driver_path)

    # Set Chrome options
    chrome_options = Options()

    # Initialize the Chrome driver with the service and options
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        for item in urls_to_check:
            try:
                if cart_status[item["url"]]:
                    print("Item already in cart, skipping...")
                    continue
                else:
                    url = item.get("url")
                    store = item.get("store")
                    driver.get(url)
                    print("--------------------------------")
                    print(f"Url {url} için: ")
                    if store == "rossmann":
                        if rossmannStockCheck(driver):
                            playsound('Crystal.mp3')
                        else:
                            print("Ürün stokta değil!!")
                    elif store == "zara":
                        # Wait for the size selector list items to load
                        print("Waiting for the size selector items to be present...")
                        wait = WebDriverWait(driver, 40)
                        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "size-selector-list__item")))

                        # Check stock for the specified sizes
                        size_in_stock = check_stock(driver, sizes_to_check)
                        if size_in_stock:
                            print(f"ALERT: The {size_in_stock} size is in stock for the product at URL: {url}")
                            playsound('Crystal.mp3')
                        else:
                            print(f"Checked {url} - no stock found for sizes {', '.join(sizes_to_check)}.")
                    else:
                        print("URL not found")
            except Exception as e:
                print(f"An error occurred with URL {url}: {e}")
    finally:
        print("Closing the browser...")
        driver.quit()

        # Sleep for a random time between the specified min and max seconds before the next check
        sleep_time = random.randint(sleep_min_seconds, sleep_max_seconds)
        print(f"Sleeping for {sleep_time // 60} minutes and {sleep_time % 60} seconds...")
        time.sleep(sleep_time)


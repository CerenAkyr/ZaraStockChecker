import json
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from playsound import playsound

# Function to check stock availability
def check_stock(driver, sizes_to_check):
    try:
        # Wait for the size selector list items to be present
        print("Waiting for the size selector items to appear...")
        wait = WebDriverWait(driver, 40)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "size-selector-list__item")))

        # Find the list items with class "size-selector-list__item"
        size_elements = driver.find_elements(By.CLASS_NAME, "size-selector-list__item")
        sizes_found = {size: False for size in sizes_to_check}

        for li in size_elements:
            try:
                # Look for the size label within each list item
                size_label = li.find_element(By.CSS_SELECTOR, "div[data-qa-qualifier='product-size-info-main-label']").text.strip()
                if size_label in sizes_to_check:
                    sizes_found[size_label] = True
                    button = li.find_element(By.CLASS_NAME, "size-selector-list__item-button")
                    if button.get_attribute("disabled"):
                        print(f"The {size_label} size button is disabled (out of stock).")
                    else:
                        print(f"The {size_label} size button is enabled (in stock).")
                        return size_label  # Return the size if found in stock
            except Exception as e:
                print(f"Error processing size element: {e}")
                continue
        
        if not any(sizes_found.values()):
            print(f"Sizes {', '.join(sizes_to_check)} not found.")
    except Exception as e:
        print(f"An error occurred during the operation: {e}")
    return None

# Load configuration from config.json
with open("config.json", "r") as config_file:
    config = json.load(config_file)

# Extract configuration values
urls_to_check = config["urls"]
sizes_to_check = config["sizes_to_check"]
sleep_min_seconds = config["sleep_min_seconds"]
sleep_max_seconds = config["sleep_max_seconds"]
chrome_driver_path = config["chrome_driver_path"]

while True:
    # Create a service object with the path to ChromeDriver from the config
    service = Service(executable_path=chrome_driver_path)

    # Set Chrome options
    chrome_options = Options()

    # Initialize the Chrome driver with the service and options
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        for url in urls_to_check:
            try:
                print(f"Opening the Zara product page: {url}")
                driver.get(url)

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
            
            except Exception as e:
                print(f"An error occurred with URL {url}: {e}")

    finally:
        print("Closing the browser...")
        driver.quit()

        # Sleep for a random time between the specified min and max seconds before the next check
        sleep_time = random.randint(sleep_min_seconds, sleep_max_seconds)
        print(f"Sleeping for {sleep_time // 60} minutes and {sleep_time % 60} seconds...")
        time.sleep(sleep_time)


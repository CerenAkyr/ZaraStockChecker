from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pygame
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import os
import sys

# Function to play sound when item is found!
def play_sound(sound_file):
    pygame.mixer.init()
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()

def get_resource_path(filename):
    """Returns the correct path for bundled files when running as an exe."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return filename


# Stock-checking logic (old main)
def stock_checker(shared_items, stock_check_event, ui):
    sleep_min_seconds = 120
    sleep_max_seconds = 240

    crystal_mp3_path = get_resource_path("Crystal.mp3")
    print("Crystal.mp3 Path:", crystal_mp3_path)


    while True:
        stock_check_event.wait()

        service = Service(ChromeDriverManager().install())
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        try:
            for item in shared_items:
                try:
                    url = item.get("link")
                    store = item.get("brand")
                    size = item.get("size")
                    driver.get(url)
                    print(f"Checking stock for URL: {url}")
                    if store.lower() == "zara":
                        size_in_stock = check_stock_zara(driver, [size])
                        if size_in_stock:
                            print(f"{size_in_stock} Beden stokta! Link: {url}")
                            message = f"{size_in_stock} Beden stokta! Link: {url}\n"
                            ui.update_status(message)
                            play_sound(crystal_mp3_path)
                        else:
                            print("No stock found.")
                            message = f"{url} linkli {size} Beden ürün için stok bulunamadı.\n"
                            ui.update_status(message)
                    elif store.lower() == "bershka":
                        size_in_stock = check_stock_bershka(driver, [size])
                        if size_in_stock:
                            print(f"{size_in_stock} Beden stokta! Link: {url}")
                            message = f"{size_in_stock} Beden stokta! Link: {url}\n"
                            ui.update_status(message)
                            play_sound(crystal_mp3_path)
                        else:
                            print("No stock found.")
                            message = f"{url} linkli {size} Beden ürün için stok bulunamadı."
                            ui.update_status(message)
                    else:
                        print(f"Unsupported store: {store}")
                except Exception as e:
                    print(f"Error checking {url}: {e}")
        finally:
            driver.quit()
            sleep_time = random.randint(sleep_min_seconds, sleep_max_seconds)
            print(f"Sleeping for {sleep_time // 60} minutes and {sleep_time % 60} seconds...")
            time.sleep(sleep_time)

# Function to check stock availability (For ZARA)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException

def check_stock_zara(driver, sizes_to_check):
    try:
        wait = WebDriverWait(driver, 60)

        # Close the cookie alert if it appears
        try:
            print("Checking for cookie alert...")
            accept_cookies_button = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            accept_cookies_button.click()
            print("Cookie alert closed successfully.")
        except TimeoutException:
            print("Cookie alert not found or already closed.")

        # Wait for "Add to Cart" button to be clickable
        try:
            add_to_cart_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-qa-action='add-to-cart']")))

            # Check if an overlay is blocking the button
            overlays = driver.find_elements(By.CLASS_NAME, "zds-backdrop")
            if overlays:
                print("Overlay detected. Attempting to remove it...")
                driver.execute_script("arguments[0].remove();", overlays[0])  # Remove overlay with JS

            # Click "Add to Cart" using JavaScript to bypass any hidden overlays
            driver.execute_script("arguments[0].click();", add_to_cart_button)
            print("Clicked 'Add to Cart' button.")
        except (TimeoutException, ElementClickInterceptedException) as e:
            print(f"Failed to click 'Add to Cart' button: {e}")
            return None

        # Wait for the size selector to appear
        print("Waiting for sizes to appear...")
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "size-selector-sizes")))

        # Find size elements
        size_elements = driver.find_elements(By.CLASS_NAME, "size-selector-sizes-size")
        sizes_found = {size: False for size in sizes_to_check}

        for li in size_elements:
            try:
                size_label = li.find_element(By.CSS_SELECTOR, "div[data-qa-qualifier='size-selector-sizes-size-label']").text.strip()
                if size_label in sizes_to_check:
                    sizes_found[size_label] = True
                    button = li.find_element(By.CLASS_NAME, "size-selector-sizes-size__button")

                    # Check if the button contains "Benzer ürünler" text
                    try:
                        similar_products_text = button.find_element(By.CLASS_NAME, "size-selector-sizes-size__action").text.strip()
                        if "Benzer ürünler" in similar_products_text:
                            print(f"The {size_label} size is out of stock and showing similar products.")
                            return False
                    except NoSuchElementException:
                        pass  # No "Benzer ürünler" text found, proceed with normal check

                    # Check stock status
                    if button.get_attribute("data-qa-action") in ["size-in-stock", "size-low-on-stock"]:
                        print(f"The {size_label} size is in stock.")
                        return size_label
                    else:
                        print(f"The {size_label} size is out of stock.")
                        return False
            except Exception as e:
                print(f"Error processing size element: {e}")
                continue

        if not any(sizes_found.values()):
            print(f"Sizes {', '.join(sizes_to_check)} not found.")
    except Exception as e:
        print(f"An error occurred during the operation: {e}")

    return None

# Function to check stock availability (For Rossmann)
def rossmannStockCheck(driver):
    wait = WebDriverWait(driver, 40)
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "product-add-form")))
    except Exception:
        print(f"Yok yok bu ürün")
        return False
    try:
        # Locate the button with the text "Sepete Ekle"
        button = driver.find_element(By.XPATH, "//button[@type='submit' and contains(., 'Sepete Ekle')]")
        if button:
            print("Rossmann ürünü stokta")
            print("Sepete eklendi!")
            driver.execute_script("arguments[0].click();", button)
            return True
    except Exception:
        print(f"Yok yok bu ürün anla yok kalmamış")
    return False

# Function to check stock availability (For Bershka)
def check_stock_bershka(driver, sizes_to_check):
    try:
        # Close the cookie alert if it appears
        try:
            print("Checking for cookie alert...")
            wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds for the alert
            accept_cookies_button = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            accept_cookies_button.click()
            print("Cookie alert closed successfully.")
        except Exception as e:
            print("Cookie alert not found or failed to close: ", e)
        
        # Proceed with the stock check
        print("Waiting for the size buttons to appear...")
        wait = WebDriverWait(driver, 40)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-qa-anchor='sizeListItem']")))

        # Find the size buttons
        size_elements = driver.find_elements(By.CSS_SELECTOR, "button[data-qa-anchor='sizeListItem']")
        sizes_found = {size: False for size in sizes_to_check}

        for button in size_elements:
            try:
                # Look for the size label within each button
                size_label = button.find_element(By.CSS_SELECTOR, "span.text__label").text.strip()
                if size_label in sizes_to_check:
                    sizes_found[size_label] = True
                    if button.get_attribute("aria-checked") == "false":
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

    
def watsonsChecker(driver):
    wait = WebDriverWait(driver, 40)
    try:
        element = wait.until(EC.presence_of_all_elements_located(By.CLASS_NAME, "product-grid-manager__view-mount"))
        text = element.text.strip()
        return not ("0 ürün") in text
    except:
        return False
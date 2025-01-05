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

# Function to play sound when item is found!
def play_sound(sound_file):
    pygame.mixer.init()
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()


# Stock-checking logic (old main)
def stock_checker(shared_items, stock_check_event, ui):
    sleep_min_seconds = 30
    sleep_max_seconds = 60

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
                            play_sound('Crystal.mp3')
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
                            play_sound('Crystal.mp3')
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
def check_stock_zara(driver, sizes_to_check):
    try:
        # Close the cookie alert if it appears
        try:
            print("Checking for cookie alert...")
            wait = WebDriverWait(driver, 60)  # Wait up to 60 seconds for the alert
            accept_cookies_button = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            accept_cookies_button.click()
            print("Cookie alert closed successfully.")
        except Exception as e:
            print("Cookie alert not found or failed to close: ", e)
        
        # Proceed with the stock check
        print("Waiting for the size selector items to appear...")
        wait = WebDriverWait(driver, 40)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "size-selector-sizes__size")))

        # Find the list items with class "size-selector-sizes__size"
        size_elements = driver.find_elements(By.CLASS_NAME, "size-selector-sizes__size")
        sizes_found = {size: False for size in sizes_to_check}

        for li in size_elements:
            try:
                # Look for the size label within each list item
                size_label = li.find_element(By.CSS_SELECTOR, "div[data-qa-qualifier='size-selector-sizes-size-label']").text.strip()
                if size_label in sizes_to_check:
                    sizes_found[size_label] = True
                    button = li.find_element(By.CLASS_NAME, "size-selector-sizes-size__button")
                    if button.get_attribute("data-qa-action") != "size-in-stock":
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
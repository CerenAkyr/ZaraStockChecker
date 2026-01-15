import json
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pygame
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os
import requests
from scraperHelpers import check_stock_zara, check_stock_bershka, check_stock_mango

with open("config.json", "r") as config_file:
    config = json.load(config_file)

urls_to_check = config["urls"]
sizes_to_check = config["sizes_to_check"]
sleep_min_seconds = config["sleep_min_seconds"]
sleep_max_seconds = config["sleep_max_seconds"]

pygame.mixer.init()

cart_status = {item["url"]: False for item in urls_to_check}

# Variable fetching for bot msg:
load_dotenv()
BOT_API = os.getenv("BOT_API")
CHAT_ID = os.getenv("CHAT_ID")

# Foolproof for not having .env and bot installed: 
if not BOT_API or not CHAT_ID:
    print("BOT_API or CHAT_ID not found in .env file. Telegram messages will be disabled.")
    TELEGRAM_ENABLED = False
else:
    TELEGRAM_ENABLED = True

# This fcn is for notification sound
def play_sound(sound_file):
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()

# This fcn is for sending messages
def send_telegram_message(message):
    if not TELEGRAM_ENABLED:
        print("Telegram message skipped (missing BOT_API or CHAT_ID).")
        return

    url = f"https://api.telegram.org/bot{BOT_API}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        print("Telegram message sent.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Telegram message: {e}")

while True:
    # Crate service & initialize
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # modern headless mode
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )

    service = Service(ChromeDriverManager().install())
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
                    
                    # --- CHANGE START ---
                    # Determine which sizes to check for THIS specific item.
                    # If the item has a "sizes" list in config, use that.
                    # Otherwise, fallback to the global "sizes_to_check" list.
                    current_sizes = item.get("sizes", sizes_to_check)
                    # --- CHANGE END ---

                    driver.get(url)
                    print("--------------------------------")
                    print(f"Url {url} için: ")
                    print(f"Checking for sizes: {current_sizes}") # Helpful log to see which sizes are being checked

                    if store == "zara":
                        # Check stock for the specific sizes (current_sizes)
                        size_in_stock = check_stock_zara(driver, current_sizes)
                        if size_in_stock:
                            message = f"🛍️{size_in_stock} beden stokta!!!!\nLink: {url}"
                            print(f"UYARI: {message}")
                            play_sound('Crystal.mp3')
                            send_telegram_message(message)
                        else:
                            print(f"{url} kontrol edildi - stok bulunamadı.")
                    elif store == "bershka":
                        size_in_stock = check_stock_bershka(driver, current_sizes)
                        if size_in_stock:
                            message = f"🛍️{size_in_stock} beden stokta!!!!\nLink: {url}"
                            print(f"UYARI: {message}")
                            play_sound('Crystal.mp3')
                            send_telegram_message(message)
                        else:
                            print(f"{url} kontrol edildi - stok bulunamadı.")
                    elif store == "mango":
                        size_in_stock = check_stock_mango(driver, current_sizes)
                        if size_in_stock:
                            message = f"🛍️{size_in_stock} beden stokta!!!!\nLink: {url}"
                            print(f"UYARI: {message}")
                            play_sound('Crystal.mp3')
                            send_telegram_message(message)
                        else:
                            print(f"{url} kontrol edildi - stok bulunamadı.")
                    else:
                        print("URL bulunamadı")
            except Exception as e:
                print(f"URL {url} ile bir hata oluştu: {e}")
    finally:
        print("Browser kapanıyor...")
        driver.quit()

        # Sleep for a random time between the specified min and max seconds before the next check
        sleep_time = random.randint(sleep_min_seconds, sleep_max_seconds)
        print(f"Sleeping for {sleep_time // 60} minutes and {sleep_time % 60} seconds...")
        time.sleep(sleep_time)
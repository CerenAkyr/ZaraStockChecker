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
from scraperHelpers import check_stock_zara, rossmannStockCheck, bershkaStockChecker

with open("config.json", "r") as config_file:
    config = json.load(config_file)

urls_to_check = config["urls"]
sizes_to_check = config["sizes_to_check"]
sleep_min_seconds = config["sleep_min_seconds"]
sleep_max_seconds = config["sleep_max_seconds"]

pygame.mixer.init()

cart_status = {item["url"]: False for item in urls_to_check}

# This part is for bot messages:
load_dotenv()
BOT_API = os.getenv("BOT_API")
CHAT_ID = os.getenv("CHAT_ID")

def play_sound(sound_file):
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_API}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("Telegram message sent.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Telegram message: {e}")


while True:
    # Crate service & initialize
    chrome_options = Options()
    # Optional: run headless
    # chrome_options.add_argument("--headless")
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
                    driver.get(url)
                    print("--------------------------------")
                    print(f"Url {url} için: ")
                    if store == "rossmann":
                        if rossmannStockCheck(driver):
                            play_sound('Crystal.mp3')
                        else:
                            print("Ürün stokta değil!!")
                    elif store == "zara":
                        # Check stock for the specified sizes
                        size_in_stock = check_stock_zara(driver, sizes_to_check)
                        if size_in_stock:
                            message = f"🛍️{size_in_stock} beden stokta!!!!\nLink: {url}"
                            print(f"ALERT: {message}")
                            play_sound('Crystal.mp3')
                            send_telegram_message(message)
                        else:
                            print(f"Checked {url} - no stock found for sizes {', '.join(sizes_to_check)}.")
                    elif store == "bershka":
                        does_exist = bershkaStockChecker(driver, sizes_to_check)
                        if does_exist:
                            print("Allaaahhh varmış stokta koş koş koş!!!")
                            play_sound('Crystal.mp3')
                        else:
                            print("Yok ablam yok :( )")
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

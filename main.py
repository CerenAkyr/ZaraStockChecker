import json
import time
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os
import requests
from scraperHelpers import check_stock_zara, check_stock_bershka, check_stock_mango

# Pygame optional - may not work on headless servers
try:
    import pygame
    pygame.mixer.init()
    SOUND_ENABLED = True
except Exception:
    print("Pygame could not be initialized - sound notifications disabled (server mode).")
    SOUND_ENABLED = False

with open("config.json", "r") as config_file:
    config = json.load(config_file)

urls_to_check = config["urls"]
sizes_to_check = config["sizes_to_check"]
sleep_min_seconds = config["sleep_min_seconds"]
sleep_max_seconds = config["sleep_max_seconds"]

cart_status = {item["url"]: False for item in urls_to_check}

# Load environment variables from .env
load_dotenv()

# Telegram config
BOT_API = os.getenv("BOT_API")
CHAT_ID = os.getenv("CHAT_ID")

# Gmail config
GMAIL_USER = os.getenv("GMAIL_USER")  # your gmail address
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")  # app password
GMAIL_TO = os.getenv("GMAIL_TO")  # recipient email address(es)

# Feature flags
if not BOT_API or not CHAT_ID:
    print("BOT_API or CHAT_ID not found in .env file. Telegram messages will be disabled.")
    TELEGRAM_ENABLED = False
else:
    TELEGRAM_ENABLED = True

if not GMAIL_USER or not GMAIL_APP_PASSWORD or not GMAIL_TO:
    print("Gmail credentials missing (.env). Email notifications disabled.")
    EMAIL_ENABLED = False
else:
    EMAIL_ENABLED = True

# Sound notification (optional)
def play_sound(sound_file):
    if not SOUND_ENABLED:
        return
    try:
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
    except Exception as e:
        print(f"Could not play sound: {e}")

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

# Send email notification
def send_email(subject, body):
    if not EMAIL_ENABLED:
        print("Email skipped (Gmail credentials missing).")
        return
    
    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = GMAIL_TO
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Send all notifications at once
def send_notification(message, subject="🛍️ Stock Alert"):
    play_sound('Crystal.mp3')
    send_telegram_message(message)
    send_email(subject, message)

while True:
    # Create service & initialize Chrome driver
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
                    driver.get(url)
                    print("--------------------------------")
                    print(f"Url {url} için: ")
                    if store == "zara":
                        size_in_stock = check_stock_zara(driver, sizes_to_check)
                        if size_in_stock:
                            message = f"🛍️ Size {size_in_stock} is in stock!!!!\nLink: {url}"
                            print(f"ALERT: {message}")
                            send_notification(message, f"ZARA - {size_in_stock} In Stock!")
                        else:
                            print(f"{url} checked - no stock found.")
                    elif store == "bershka":
                        size_in_stock = check_stock_bershka(driver, sizes_to_check)
                        if size_in_stock:
                            message = f"🛍️ Size {size_in_stock} is in stock!!!!\nLink: {url}"
                            print(f"ALERT: {message}")
                            send_notification(message, f"BERSHKA - {size_in_stock} In Stock!")
                        else:
                            print(f"{url} checked - no stock found.")
                    elif store == "mango":
                        size_in_stock = check_stock_mango(driver, sizes_to_check)
                        if size_in_stock:
                            message = f"🛍️ Size {size_in_stock} is in stock!!!!\nLink: {url}"
                            print(f"ALERT: {message}")
                            send_notification(message, f"MANGO - {size_in_stock} In Stock!")
                        else:
                            print(f"{url} checked - no stock found.")
                    else:
                        print("URL not found")
            except Exception as e:
                print(f"An error occurred with URL {url}: {e}")
    finally:
        print("Closing browser...")
        driver.quit()

        # Sleep for a random time between the specified min and max seconds before the next check
        sleep_time = random.randint(sleep_min_seconds, sleep_max_seconds)
        print(f"Sleeping for {sleep_time // 60} minutes and {sleep_time % 60} seconds...")
        time.sleep(sleep_time)

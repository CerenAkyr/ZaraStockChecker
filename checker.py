import json
import os
import random
import sys
import time

import pygame
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from scraperHelpers import check_stock_bershka, check_stock_mango, check_stock_zara


def get_resource_path(relative_path):
    if getattr(sys, "frozen", False):
        base_path = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def load_config(config_path):
    with open(get_resource_path(config_path), "r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    required_keys = ["urls", "sleep_min_seconds", "sleep_max_seconds"]
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise ValueError(f"Missing required config keys: {', '.join(missing_keys)}")

    return config


def normalize_size(size):
    normalized = str(size).strip()
    if normalized in {"-", "bedensiz"}:
        return "-"
    return normalized.upper()


def resolve_item_sizes(item, fallback_sizes=None):
    sizes = item.get("sizes")
    if sizes:
        return [normalize_size(size) for size in sizes]
    if fallback_sizes:
        return [normalize_size(size) for size in fallback_sizes]
    return []


def initialize_sound(log):
    try:
        pygame.mixer.init()
        return True
    except pygame.error as exc:
        log(f"Sound disabled: {exc}")
        return False


def play_sound(sound_file, log):
    try:
        pygame.mixer.music.load(get_resource_path(sound_file))
        pygame.mixer.music.play()
    except Exception as exc:
        log(f"Sound error: {exc}")


def send_telegram_message(message, bot_api, chat_id, log):
    if not bot_api or not chat_id:
        log("Telegram message skipped (missing BOT_API or CHAT_ID).")
        return

    url = f"https://api.telegram.org/bot{bot_api}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        log("Telegram message sent.")
    except requests.exceptions.RequestException as exc:
        log(f"Failed to send Telegram message: {exc}")


def _sleep_with_stop(total_seconds, stop_event):
    remaining = total_seconds
    while remaining > 0:
        if stop_event and stop_event.is_set():
            return False
        time.sleep(min(1, remaining))
        remaining -= 1
    return True


def run_checker(
    stop_event=None,
    log=print,
    items=None,
    sizes=None,
    sleep_min_seconds=None,
    sleep_max_seconds=None,
    bot_api=None,
    chat_id=None,
    play_sound_on_found=True,
    config_path="config.json",
):
    config = None
    provided_items = items or []
    needs_config_fallback = items is None or sleep_min_seconds is None or sleep_max_seconds is None
    if not needs_config_fallback and sizes is None:
        needs_config_fallback = any(
            not item.get("sizes") for item in provided_items if isinstance(item, dict)
        )

    if needs_config_fallback:
        config = load_config(config_path)

    urls_to_check = items if items is not None else config["urls"]
    sizes_to_check = sizes if sizes is not None else config.get("sizes_to_check", [])
    sleep_min_seconds = (
        sleep_min_seconds if sleep_min_seconds is not None else config["sleep_min_seconds"]
    )
    sleep_max_seconds = (
        sleep_max_seconds if sleep_max_seconds is not None else config["sleep_max_seconds"]
    )

    sound_enabled = initialize_sound(log) if play_sound_on_found else False

    if bot_api is None or chat_id is None:
        load_dotenv()
        bot_api = bot_api or os.getenv("BOT_API")
        chat_id = chat_id or os.getenv("CHAT_ID")

    if not bot_api or not chat_id:
        log("BOT_API or CHAT_ID not found in .env file. Telegram messages will be disabled.")

    while True:
        if stop_event and stop_event.is_set():
            log("Stopping...")
            return

        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        try:
            for item in urls_to_check:
                if stop_event and stop_event.is_set():
                    log("Stopping...")
                    return

                url = item.get("url")
                try:
                    if not url:
                        log("Skipping item with missing URL.")
                        continue

                    store = item.get("store")
                    driver.get(url)
                    log("--------------------------------")
                    log(f"Url {url} için: ")

                    item_sizes = resolve_item_sizes(item, sizes_to_check)
                    if not item_sizes:
                        log(f"Skipping {url}: no size configured for this item.")
                        continue

                    if store == "zara":
                        size_in_stock = check_stock_zara(driver, item_sizes)
                    elif store == "bershka":
                        size_in_stock = check_stock_bershka(driver, item_sizes)
                    elif store == "mango":
                        size_in_stock = check_stock_mango(driver, item_sizes)
                    else:
                        log("URL bulunamadı")
                        continue

                    if size_in_stock:
                        message = f"🛍️{size_in_stock} beden stokta!!!!\nLink: {url}"
                        log(f"UYARI: {message}")
                        if sound_enabled:
                            play_sound("Crystal.mp3", log)
                        send_telegram_message(message, bot_api, chat_id, log)
                    else:
                        log(f"{url} kontrol edildi - stok bulunamadı.")
                except Exception as exc:
                    log(f"URL {url} ile bir hata oluştu: {exc}")
        finally:
            log("Browser kapanıyor...")
            driver.quit()

        sleep_time = random.randint(sleep_min_seconds, sleep_max_seconds)
        log(f"Sleeping for {sleep_time // 60} minutes and {sleep_time % 60} seconds...")
        if not _sleep_with_stop(sleep_time, stop_event):
            log("Stopping...")
            return

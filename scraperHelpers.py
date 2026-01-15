from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import pygame
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import os
import sys

def check_stock_zara(driver, sizes_to_check):
    try:
        wait = WebDriverWait(driver, 60)
        
        try:
            accept_cookies_button = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            accept_cookies_button.click()
        except TimeoutException:
            pass

        try:
            add_to_cart_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-qa-action='add-to-cart']")))
            overlays = driver.find_elements(By.CLASS_NAME, "zds-backdrop")
            if overlays:
                driver.execute_script("arguments[0].remove();", overlays[0])
            driver.execute_script("arguments[0].click();", add_to_cart_button)
        except (TimeoutException, ElementClickInterceptedException):
            return None

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "size-selector-sizes")))

        size_elements = driver.find_elements(By.CLASS_NAME, "size-selector-sizes-size")
        
        found_in_stock = [] 

        for li in size_elements:
            try:
                size_label = li.find_element(By.CSS_SELECTOR, "div[data-qa-qualifier='size-selector-sizes-size-label']").text.strip()
                
                if size_label in sizes_to_check:
                    button = li.find_element(By.CLASS_NAME, "size-selector-sizes-size__button")
                    
                    try:
                        similar_text = button.find_element(By.CLASS_NAME, "size-selector-sizes-size__action").text.strip()
                        if "Benzer ürünler" in similar_text:
                            continue 
                    except NoSuchElementException:
                        pass 

                    if button.get_attribute("data-qa-action") in ["size-in-stock", "size-low-on-stock"]:
                        print(f"Found stock for: {size_label}")
                        found_in_stock.append(size_label) 
                    else:
                        print(f"{size_label} is out of stock.")

            except Exception:
                continue

        if len(found_in_stock) > 0:
            return ", ".join(found_in_stock)
        
        return None

    except Exception as e:
        print(f"An error occurred: {e}")
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


def check_stock_bershka(driver, sizes_to_check):
    try:
        wait = WebDriverWait(driver, 10)

        try:
            accept_cookies_button = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            accept_cookies_button.click()
        except Exception:
            pass

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-qa-anchor='productDetailSize']")))
        time.sleep(2)

        size_buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-qa-anchor='sizeListItem']")
        #collect all sizes
        found_in_stock = []
        sizes_found_on_page = False

        for button in size_buttons:
            try:
                size_label_elem = button.find_element(By.CSS_SELECTOR, "span.text__label")
                size_label = size_label_elem.text.strip()

                if size_label in sizes_to_check:
                    sizes_found_on_page = True
                    
                    class_attr = button.get_attribute("class") or ""
                    aria_disabled = button.get_attribute("aria-disabled") == "true"
                    is_disabled_attr = button.get_attribute("disabled") is not None
                    is_disabled = "is-disabled" in class_attr or aria_disabled or is_disabled_attr

                    if not is_disabled:
                        print(f"Bershka: {size_label} is in stock!")
                        found_in_stock.append(size_label)
                    else:
                        print(f"Bershka: {size_label} is out of stock.")

            except Exception:
                continue

        if not sizes_found_on_page:
            print(f"⚠️ Sizes {', '.join(sizes_to_check)} not found on page.")
            return None

        if found_in_stock:
            return ", ".join(found_in_stock)
            
        return False

    except Exception as e:
        print(f"An error occurred while checking Bershka stock: {e}")
    
    return None


# Function to check stock availability for Mango
def check_stock_mango(driver, sizes_to_check):
    try:
        wait = WebDriverWait(driver, 15)

        try:
            accept = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            accept.click()
        except Exception:
            pass

        try:
            wait.until(
                EC.any_of(
                    EC.presence_of_element_located((By.ID, "pdp-size-selector")),
                    EC.presence_of_element_located((By.ID, "pdp-primary-actions"))
                )
            )
        except TimeoutException:
            return None

        size_selectors = [
            "button[id^='pdp.productInfo.sizeSelector.size']",
            "p[id^='pdp.productInfo.sizeSelector.size']",
        ]
        size_elements = []
        for sel in size_selectors:
            size_elements.extend(driver.find_elements(By.CSS_SELECTOR, sel))

        def extract_label(el):
            try:
                label_el = el.find_element(By.CSS_SELECTOR, "span.textActionM_className__8McJk")
                label = label_el.text.strip()
                if label.lower() in ["standart", "standard"]: return "bedensiz"
                return label
            except Exception:
                text = el.text.strip()
                if text.lower() in ["standart", "standard"]: return "bedensiz"
                return text

        found_in_stock = []

        if size_elements:
            sizes_found_on_page = False
            
            for el in size_elements:
                try:
                    label = extract_label(el)

                    if label in sizes_to_check:
                        sizes_found_on_page = True
                        
                        el_id = el.get_attribute("id") or ""
                        aria_disabled = el.get_attribute("aria-disabled")
                        is_disabled_attr = (el.get_attribute("disabled") is not None)

                        available_by_id = "sizeAvailable" in el_id and "sizeUnavailable" not in el_id
                        enabled_state = not (aria_disabled == "true" or is_disabled_attr)

                        if available_by_id and enabled_state:
                            print(f"Mango: {label} is in stock!")
                            found_in_stock.append(label)
                        else:
                            print(f"Mango: {label} is out of stock.")
                except Exception:
                    continue
            
            if found_in_stock:
                return ", ".join(found_in_stock)
                
            if sizes_found_on_page:
                return False

        # "Bedensiz" (Standard size) Logic
        if "bedensiz" in sizes_to_check:
            try:
                actions = driver.find_element(By.ID, "pdp-primary-actions")
                add_buttons = actions.find_elements(By.CSS_SELECTOR, "button.ButtonPrimary_default__2Mbr8, button[aria-disabled]")
                if not add_buttons:
                    add_buttons = actions.find_elements(By.TAG_NAME, "button")

                add_enabled = False
                for btn in add_buttons:
                    try:
                        label = (btn.text or "").strip().lower()
                        aria_disabled = btn.get_attribute("aria-disabled")
                        if ("ekle" in label or "add" in label or label == "") and aria_disabled != "true":
                            add_enabled = True
                            break
                    except Exception:
                        continue

                if add_enabled:
                    return "bedensiz"
                else:
                    return False
            except Exception:
                pass

        return None
    except Exception as e:
        print(f"An error occurred while checking Mango stock: {e}")
        return None
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

# Function to check stock availability (For ZARA)
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
        any_in_stock = None

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
                            any_in_stock = False if any_in_stock is None else any_in_stock
                            continue
                    except NoSuchElementException:
                        pass  # No "Benzer ürünler" text found, proceed with normal check

                    # Check stock status
                    if button.get_attribute("data-qa-action") in ["size-in-stock", "size-low-on-stock"]:
                        print(f"The {size_label} size is in stock.")
                        return size_label
                    else:
                        print(f"The {size_label} size is out of stock.")
                        any_in_stock = False if any_in_stock is None else any_in_stock
                        continue
            except Exception as e:
                print(f"Error processing size element: {e}")
                continue

        if not any(sizes_found.values()):
            print(f"Sizes {', '.join(sizes_to_check)} not found.")
            return None

        # At least one requested size was present but none were in stock
        if any_in_stock is False:
            return False
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


def check_stock_bershka(driver, sizes_to_check):
    try:
        wait = WebDriverWait(driver, 10)

        # Handle cookie popup if present
        try:
            print("Checking for cookie alert...")
            accept_cookies_button = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            accept_cookies_button.click()
            print("Cookie alert closed.")
        except Exception:
            print("No cookie alert or already closed.")

        # Wait for the size list to load (dot list or legacy list)
        print("Waiting for the size list...")
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[data-qa-anchor='productDetailSize']")
            )
        )

        # Allow extra time for dynamic class updates to finish
        time.sleep(10)

        size_buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-qa-anchor='sizeListItem']")
        sizes_found = {size: False for size in sizes_to_check}
        any_in_stock = None

        for button in size_buttons:
            try:
                size_label_elem = button.find_element(By.CSS_SELECTOR, "span.text__label")
                size_label = size_label_elem.text.strip()

                if size_label in sizes_to_check:
                    sizes_found[size_label] = True

                    class_attr = button.get_attribute("class") or ""
                    aria_disabled = button.get_attribute("aria-disabled") == "true"
                    is_disabled_attr = button.get_attribute("disabled") is not None
                    is_disabled = "is-disabled" in class_attr or aria_disabled or is_disabled_attr

                    if is_disabled:
                        print(f"{size_label} is out of stock.")
                        any_in_stock = False if any_in_stock is None else any_in_stock
                    else:
                        print(f"{size_label} is in stock!")
                        return size_label
            except Exception as e:
                print(f"Error processing size button: {e}")
                continue

        if not any(sizes_found.values()):
            print(f"⚠️ Sizes {', '.join(sizes_to_check)} not found.")
            return None
        if any_in_stock is False:
            return False
    except Exception as e:
        print(f"An error occurred while checking Bershka stock: {e}")

    return None
    
def watsonsChecker(driver):
    wait = WebDriverWait(driver, 40)
    try:
        element = wait.until(EC.presence_of_all_elements_located(By.CLASS_NAME, "product-grid-manager__view-mount"))
        text = element.text.strip()
        return not ("0 ürün") in text
    except:
        return False


# Function to check stock availability for Mango
def check_stock_mango(driver, sizes_to_check):
    try:
        wait = WebDriverWait(driver, 15)

        # Best-effort cookie accept
        try:
            print("Checking for cookie alert...")
            accept = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            accept.click()
            print("Cookie alert closed.")
        except Exception:
            print("No cookie alert or already closed.")

        # Wait for either size selector or actions to be present
        try:
            wait.until(
                EC.any_of(
                    EC.presence_of_element_located((By.ID, "pdp-size-selector")),
                    EC.presence_of_element_located((By.ID, "pdp-primary-actions"))
                )
            )
        except TimeoutException:
            print("Mango PDP did not expose size selector or actions in time.")
            return None

        # Collect potential size items (buttons or <p> for no-size/standard)
        size_selectors = [
            "button[id^='pdp.productInfo.sizeSelector.size']",
            "p[id^='pdp.productInfo.sizeSelector.size']",
        ]
        size_elements = []
        for sel in size_selectors:
            size_elements.extend(driver.find_elements(By.CSS_SELECTOR, sel))

        # Helper to extract label text from a size element
        def extract_label(el):
            try:
                label_el = el.find_element(By.CSS_SELECTOR, "span.textActionM_className__8McJk")
                label = label_el.text.strip()
                # Map Standard/no-size to config keyword when appropriate
                if label.lower() in ["standart", "standard"]:
                    return "bedensiz"
                return label
            except Exception:
                # Fallback to element text
                text = el.text.strip()
                if text.lower() in ["standart", "standard"]:
                    return "bedensiz"
                return text

        # If we have size elements, try to match against sizes_to_check
        if size_elements:
            sizes_found = {size: False for size in sizes_to_check}

            for el in size_elements:
                try:
                    label = extract_label(el)

                    if label in sizes_to_check:
                        sizes_found[label] = True

                        el_id = el.get_attribute("id") or ""
                        aria_disabled = el.get_attribute("aria-disabled")
                        is_disabled_attr = (el.get_attribute("disabled") is not None)

                        # Availability signals: id contains 'sizeAvailable' and element not disabled
                        available_by_id = "sizeAvailable" in el_id and "sizeUnavailable" not in el_id
                        enabled_state = not (aria_disabled == "true" or is_disabled_attr)

                        if available_by_id and enabled_state:
                            print(f"{label} is in stock!")
                            return label
                        else:
                            print(f"{label} is out of stock.")
                            # Keep checking others; if none available, we will return False
                except Exception as e:
                    print(f"Error processing Mango size element: {e}")
                    continue

            if not any(sizes_found.values()):
                print(f"Sizes {', '.join(sizes_to_check)} not found on Mango PDP.")
                return None

            # At least one requested size was present but not available
            return False

        # No explicit size elements: treat as no-size product
        if "bedensiz" in sizes_to_check:
            try:
                # Determine if 'Add to bag' is enabled
                # Prefer the primary actions container first
                actions = driver.find_element(By.ID, "pdp-primary-actions")
                add_buttons = actions.find_elements(By.CSS_SELECTOR, "button.ButtonPrimary_default__2Mbr8, button[aria-disabled]")
                # Fallback: any button with text content indicative of add
                if not add_buttons:
                    add_buttons = actions.find_elements(By.TAG_NAME, "button")

                add_enabled = False
                for btn in add_buttons:
                    try:
                        label = (btn.text or "").strip().lower()
                        aria_disabled = btn.get_attribute("aria-disabled")
                        if ("ekle" in label or label == "" or "add" in label) and aria_disabled != "true":
                            add_enabled = True
                            break
                    except Exception:
                        continue

                if add_enabled:
                    print("No size selector; 'Add to bag' enabled -> bedensiz in stock!")
                    return "bedensiz"
                else:
                    print("No size selector; 'Add to bag' disabled -> out of stock for bedensiz.")
                    return False
            except Exception as e:
                print(f"Mango no-size flow check failed: {e}")
                return None

        # No size elements and 'bedensiz' not requested -> not applicable
        print("No sizes found and 'bedensiz' not requested in config.")
        return None
    except Exception as e:
        print(f"An error occurred while checking Mango stock: {e}")
        return None

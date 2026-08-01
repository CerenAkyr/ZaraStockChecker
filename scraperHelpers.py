import time

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


NO_SIZE_MARKER = "-"


def _has_no_size_option(sizes_to_check):
    return NO_SIZE_MARKER in sizes_to_check


def _matches_requested_size(requested_size, displayed_size):
    requested = (requested_size or "").strip().upper()
    displayed = (displayed_size or "").strip().upper()
    if requested == displayed:
        return True

    normalized_displayed = displayed.replace("(", " ").replace(")", " ").replace("/", " ")
    normalized_displayed = normalized_displayed.replace("-", " ")
    tokens = {token for token in normalized_displayed.split() if token}
    return requested in tokens


def check_stock_zara(driver, sizes_to_check):
    try:
        wait = WebDriverWait(driver, 60)

        try:
            print("Checking for cookie alert...")
            accept_cookies_button = wait.until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            accept_cookies_button.click()
            print("Cookie alert closed successfully.")
        except TimeoutException:
            print("Cookie alert not found or already closed.")

        try:
            add_to_cart_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-qa-action='add-to-cart']"))
            )

            overlays = driver.find_elements(By.CLASS_NAME, "zds-backdrop")
            if overlays:
                print("Overlay detected. Attempting to remove it...")
                driver.execute_script("arguments[0].remove();", overlays[0])

            driver.execute_script("arguments[0].click();", add_to_cart_button)
            print("Clicked 'Add to Cart' button.")
        except (TimeoutException, ElementClickInterceptedException) as exc:
            print(f"Failed to click 'Add to Cart' button: {exc}")
            return None

        if _has_no_size_option(sizes_to_check):
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "shop-cart"))
                )
                print("No-size Zara item appears to be addable to cart.")
                return NO_SIZE_MARKER
            except TimeoutException:
                pass

        print("Waiting for sizes to appear...")
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "size-selector-sizes")))

        size_elements = driver.find_elements(By.CLASS_NAME, "size-selector-sizes-size")
        sizes_found = {size: False for size in sizes_to_check}
        any_in_stock = None

        for li in size_elements:
            try:
                size_label = li.find_element(
                    By.CSS_SELECTOR, "div[data-qa-qualifier='size-selector-sizes-size-label']"
                ).text.strip()
                matched_size = next(
                    (size for size in sizes_to_check if _matches_requested_size(size, size_label)),
                    None,
                )
                if matched_size:
                    sizes_found[matched_size] = True
                    button = li.find_element(By.CLASS_NAME, "size-selector-sizes-size__button")

                    try:
                        similar_products_text = button.find_element(
                            By.CLASS_NAME, "size-selector-sizes-size__action"
                        ).text.strip()
                        if any(
                            text in similar_products_text
                            for text in ["Benzer ürünler", "Ähnliche Produkte", "Similar products"]
                        ):
                            print(f"The {size_label} size is out of stock and showing similar products.")
                            any_in_stock = False if any_in_stock is None else any_in_stock
                            continue
                    except NoSuchElementException:
                        pass

                    if button.get_attribute("data-qa-action") in ["size-in-stock", "size-low-on-stock"]:
                        print(f"The {size_label} size is in stock.")
                        return matched_size
                    print(f"The {size_label} size is out of stock.")
                    any_in_stock = False if any_in_stock is None else any_in_stock
            except Exception as exc:
                print(f"Error processing size element: {exc}")

        if not any(sizes_found.values()):
            print(f"Sizes {', '.join(sizes_to_check)} not found.")
            return None

        if any_in_stock is False:
            return False
    except Exception as exc:
        print(f"An error occurred during the operation: {exc}")

    return None


def check_stock_bershka(driver, sizes_to_check):
    try:
        wait = WebDriverWait(driver, 20)

        try:
            print("Checking for cookie alert...")
            accept_cookies_button = wait.until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            driver.execute_script("arguments[0].click();", accept_cookies_button)
            print("Cookie alert closed.")
        except Exception:
            print("No cookie alert or already closed.")

        if _has_no_size_option(sizes_to_check):
            add_buttons = driver.find_elements(
                By.CSS_SELECTOR,
                "button[data-qa-anchor='addToCart'], button[type='submit'], button[class*='add-to-cart'], button[class*='addToCart']",
            )
            for button in add_buttons:
                class_attr = button.get_attribute("class") or ""
                aria_disabled = button.get_attribute("aria-disabled") == "true"
                is_disabled_attr = button.get_attribute("disabled") is not None
                if not ("is-disabled" in class_attr or aria_disabled or is_disabled_attr):
                    print("No-size Bershka item appears to be addable to cart.")
                    return NO_SIZE_MARKER

        print("Waiting for Bershka size buttons...")
        size_buttons = wait.until(
            EC.presence_of_all_elements_located(
                (
                    By.CSS_SELECTOR,
                    ".size-selector__list button.size-button, "
                    ".size-selector__dimension button.size-button, "
                    ".size-button-wrapper button.size-button, "
                    "button[data-qa-anchor='sizeListItem'], "
                    "[data-qa-anchor='productDetailSize'] [role='button']",
                )
            )
        )
        sizes_found = {size: False for size in sizes_to_check}
        any_in_stock = None

        for button in size_buttons:
            try:
                size_label = ""
                label_selectors = [
                    "span.size-button__label",
                    "span.text__label",
                    "span[class*='text__label']",
                    "span",
                    "div",
                ]
                for selector in label_selectors:
                    label_elements = button.find_elements(By.CSS_SELECTOR, selector)
                    for element in label_elements:
                        candidate = (element.text or "").strip()
                        if candidate:
                            size_label = candidate
                            break
                    if size_label:
                        break

                if not size_label:
                    size_label = (button.text or "").strip()
                size_label = size_label.splitlines()[0].strip()

                if size_label in sizes_to_check:
                    sizes_found[size_label] = True

                    class_attr = button.get_attribute("class") or ""
                    aria_disabled = button.get_attribute("aria-disabled") == "true"
                    is_disabled_attr = button.get_attribute("disabled") is not None
                    is_disabled = (
                        "size-button--disabled" in class_attr
                        or "is-disabled" in class_attr
                        or aria_disabled
                        or is_disabled_attr
                    )

                    if is_disabled:
                        print(f"{size_label} is out of stock.")
                        any_in_stock = False if any_in_stock is None else any_in_stock
                    else:
                        print(f"{size_label} is in stock!")
                        return size_label
            except Exception as exc:
                print(f"Error processing size button: {type(exc).__name__}: {exc}")

        if not any(sizes_found.values()):
            print(f"⚠️ Sizes {', '.join(sizes_to_check)} not found.")
            return None
        if any_in_stock is False:
            return False
    except Exception as exc:
        print(f"An error occurred while checking Bershka stock: {type(exc).__name__}: {exc}")

    return None


def check_stock_mango(driver, sizes_to_check):
    try:
        wait = WebDriverWait(driver, 15)

        try:
            print("Checking for cookie alert...")
            accept = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            accept.click()
            print("Cookie alert closed.")
        except Exception:
            print("No cookie alert or already closed.")

        try:
            wait.until(
                EC.any_of(
                    EC.presence_of_element_located((By.ID, "pdp-size-selector")),
                    EC.presence_of_element_located((By.ID, "pdp-primary-actions")),
                )
            )
        except TimeoutException:
            print("Mango PDP did not expose size selector or actions in time.")
            return None

        size_selectors = [
            "#pdp-size-selector button[id^='product.sizeSelector.']",
            "#pdp-size-selector button[id^='pdp.productInfo.sizeSelector.size']",
            "#pdp-size-selector p[id^='product.sizeSelector.']",
            "#pdp-size-selector p[id^='pdp.productInfo.sizeSelector.size']",
        ]
        size_elements = []
        for sel in size_selectors:
            size_elements.extend(driver.find_elements(By.CSS_SELECTOR, sel))

        def extract_label(el):
            try:
                label_el = el.find_element(
                    By.CSS_SELECTOR,
                    "[class*='SizeLabel-module'][class*='withElipsis'], "
                    "span[class*='textActionM-module'], "
                    "span",
                )
                label = label_el.text.strip()
                if label.lower() in ["standart", "standard"]:
                    return NO_SIZE_MARKER
                return label
            except Exception:
                text = el.text.strip()
                if text.lower() in ["standart", "standard"]:
                    return NO_SIZE_MARKER
                return text

        if size_elements:
            sizes_found = {size: False for size in sizes_to_check}

            for el in size_elements:
                try:
                    label = extract_label(el)

                    if label in sizes_to_check:
                        sizes_found[label] = True

                        el_id = el.get_attribute("id") or ""
                        aria_disabled = el.get_attribute("aria-disabled")
                        is_disabled_attr = el.get_attribute("disabled") is not None

                        available_by_id = ".available." in el_id or "sizeAvailable" in el_id
                        enabled_state = not (aria_disabled == "true" or is_disabled_attr)

                        if available_by_id and enabled_state:
                            print(f"{label} is in stock!")
                            return label
                        print(f"{label} is out of stock.")
                except Exception as exc:
                    print(f"Error processing Mango size element: {exc}")

            if not any(sizes_found.values()):
                print(f"Sizes {', '.join(sizes_to_check)} not found on Mango PDP.")
                return None

            return False

        if _has_no_size_option(sizes_to_check):
            try:
                actions = driver.find_element(By.ID, "pdp-primary-actions")
                add_buttons = actions.find_elements(
                    By.CSS_SELECTOR, "button.ButtonPrimary_default__2Mbr8, button[aria-disabled]"
                )
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
                    print("No size selector; 'Add to bag' enabled -> no-size item in stock!")
                    return NO_SIZE_MARKER
                print("No size selector; 'Add to bag' disabled -> out of stock for no-size item.")
                return False
            except Exception as exc:
                print(f"Mango no-size flow check failed: {exc}")
                return None

        print("No sizes found and no-size marker '-' was not requested in config.")
        return None
    except Exception as exc:
        print(f"An error occurred while checking Mango stock: {exc}")
        return None

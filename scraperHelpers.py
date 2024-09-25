from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Function to check stock availability (For ZARA)
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
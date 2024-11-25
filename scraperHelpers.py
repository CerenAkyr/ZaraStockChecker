from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Function to check stock availability (For ZARA)
def check_stock(driver, sizes_to_check):
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

def bershkaStockChecker(driver, sizes_to_check):
    try:
        # Locate all size elements within the listbox
        size_elements = driver.find_elements(By.CSS_SELECTOR, 'ul[role="listbox"] li button[data-qa-anchor="sizeListItem"]')
        
        for size_element in size_elements:
            # Get the aria-label attribute to determine the size
            size_label = size_element.get_attribute('aria-label')
            
            # Check if the size is in the sizes_to_check list
            if size_label in sizes_to_check:
                # Check if the element does not have the 'is-disabled' class
                is_disabled = size_element.get_attribute('class')
                if 'is-disabled' not in is_disabled:
                    return True  # Size is in stock
        return False  # None of the sizes in sizes_to_check are in stock
    except Exception as error:
        print(f"Error while checking stock: {error}")
        return False
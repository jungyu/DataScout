from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

def scrape_website(url, element_id, timeout=10):
    """
    Scrapes a website for a specific element by its ID.

    Args:
        url (str): The URL of the website to scrape.
        element_id (str): The ID of the element to find.
        timeout (int): The maximum time to wait for the element to appear (in seconds).

    Returns:
        str: The text content of the found element, or None if the element is not found.
    """
    try:
        driver = webdriver.Chrome()
        driver.get(url)

        wait = WebDriverWait(driver, timeout)
        element = wait.until(EC.presence_of_element_located((By.ID, element_id)))

        return element.text
    except TimeoutException:
        print(f"Timeout: Element with ID '{element_id}' not found within {timeout} seconds.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        driver.quit()

if __name__ == "__main__":
    target_url = "https://www.example.com"
    target_element_id = "some_element_id"
    result = scrape_website(target_url, target_element_id)
    if result:
        print(f"Found element text: {result}")

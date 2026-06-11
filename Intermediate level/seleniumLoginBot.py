from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# --- Configuration ---
# IMPORTANT: Replace these placeholders with the actual details of the 
website you are targeting!
URL = "https://demo.selenium.io/login/" # Example URL
USERNAME = "your_username_here"        # Change this to your target 
username
PASSWORD = "your_password_here"        # Change this to your target 
password

def login_bot():
    print("--- Starting Selenium Login Bot ---")
    
    # 1. Setup the WebDriver (This assumes ChromeDriver is accessible)
    try:
        # Initialize the Chrome driver
        driver = webdriver.Chrome()
        print("Browser successfully initialized.")
        
        # Set an explicit wait for elements to load (Best practice!)
        wait = WebDriverWait(driver, 10)

        # 2. Navigate to the URL
        driver.get(URL)
        print(f"Navigating to: {URL}")
        
        # Give the page time to load completely
        time.sleep(2) 

        try:
            # --- 3. Locate and Input Username ---
            # NOTE: You must inspect the target website to find the 
correct ID/Name.
            # Here we assume the username field has an 'id' attribute 
named 'username_field'.
            username_field = 
wait.until(EC.presence_of_element_by_id("username_field"))
            print("Found Username field. Entering data...")
            username_field.send_keys(USERNAME)

            # --- 4. Locate and Input Password ---
            # Here we assume the password field has an 'id' attribute 
named 'password_field'.
            password_field = driver.find_element(By.ID, "password_field")
            print("Found Password field. Entering data...")
            password_field.send_keys(PASSWORD)

            # --- 5. Locate and Click Login Button ---
            # Here we assume the login button has an 'id' attribute named 
'login_button'.
            login_button = driver.find_element(By.ID, "login_button")
            print("Clicking Login button...")
            login_button.click()

            # Wait for a result to appear before closing
            time.sleep(5) 
            print("\nLogin process attempted successfully!")

        except Exception as e:
            print(f"\n❌ An error occurred during the login process:")
            print(f"Error details: {e}")
            print("Please check if your selectors (IDs/Names) are correct 
for the target website.")
            
    except Exception as e:
        print(f"\n❌ A major error occurred during WebDriver setup or 
navigation:")
        print(f"Error details: {e}")

    finally:
        # 6. Close the browser session
        if 'driver' in locals():
            print("\nClosing browser.")
            driver.quit()

if __name__ == "__main__":
    login_bot()
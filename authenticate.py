import os
import subprocess
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

load_dotenv()

chrome = subprocess.Popen(
    [
        "google-chrome-stable",
        "--headless",
        "--remote-debugging-port=9222",
        "--user-data-dir=/home/wavefire/.config/google-chrome",
    ]
)

chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
driver = webdriver.Chrome(options=chrome_options)

# Go to canvas
print("Going to canvas")
driver.get("https://utexas.instructure.com")
time.sleep(5)

# Authenticate (TODO:need to figure out what happens if DUO is required)
print(f"Authenticating with {os.getenv('UTEID')}")
driver.find_element("name", "j_username").send_keys(os.getenv("UTEID"))
driver.find_element("name", "j_password").send_keys(os.getenv("UTPWD"))
driver.find_element("name", "_eventId_proceed").click()
time.sleep(5)

# Check for DUO auth
try:
    verification_code = driver.find_element("class name", "verification-code")
    print(f"Enter this code on your phone: {verification_code.text}")
    # Wait for user to confirm DUO auth
    input("Press Enter after you've completed DUO authentication...")
except None:
    print("No DUO authentication required")

# Go to lectures online (authenticates as a byproduct of going to the page)
print("Going to lectures online")
driver.get(
    "https://utexas.instructure.com/courses/1414930/external_tools/143760?display=borderless"
)
print(driver.page_source)
time.sleep(2)

driver.quit()
# chrome.kill()

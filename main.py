import sys
import time
import random
from playwright.sync_api import sync_playwright
import os
import dotenv

dotenv.load_dotenv()

action = sys.argv[1]  


delay_seconds = random.randint(0, 600)
time.sleep(delay_seconds) 

with sync_playwright() as pw:
    browser = pw.firefox.launch(headless=False)
    page = browser.new_page()
    page.goto("https://payroll.razorpay.com/login?redirect=%2Fdashboard")

    page.get_by_placeholder("Enter your email address").fill(os.getenv("email"))
    page.locator("#password").fill(os.getenv("password"))  
    page.locator("#loginButton").click()  

    page.wait_for_timeout(5000)     
    page.get_by_text("Attendance").first.click()
    page.wait_for_timeout(5000)

    if action == "checkin":
        checkin_button = page.get_by_role("button", name="Check In") 
        if checkin_button.is_enabled() and checkin_button.is_visible():
            checkin_button.click()
    elif action == "checkout":
        page.get_by_role("button", name="Check Out").click()

    page.wait_for_timeout(2000)     
    browser.close()
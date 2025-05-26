import sys
import time
import os
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def wait(seconds=10):
    print(f"Waiting for {seconds} seconds...")
    time.sleep(seconds)

def log(msg):
    print(f"[LOG] {msg}")

action = sys.argv[1]  # "checkin" or "checkout"

with sync_playwright() as pw:
    browser = pw.firefox.launch(headless=False, slow_mo=50)
    
    context = browser.new_context(
        permissions=["geolocation"],  # Allow geolocation permission
        geolocation={"latitude": 12.91189, "longitude": 77.60078},
        locale="en-US"
    )
    
    page = context.new_page()

    try:
        log("Navigating to login page...")
        page.goto("https://payroll.razorpay.com/login?redirect=%2Fdashboard")
        wait()

        log("Filling credentials...")
        page.get_by_placeholder("Enter your email address").fill(os.environ["email"])
        page.locator("#password").fill(os.environ["password"])
        page.locator("#loginButton").click()
        wait()

        log("Waiting for dashboard...")
        page.wait_for_load_state("networkidle")
        wait()

        log("Clicking 'Attendance'...")
        try:
            attendance = page.get_by_text("Attendance").first
            attendance.click()
        except PlaywrightTimeoutError:
            log("Attendance tab not clickable.")
            page.screenshot(path="error_attendance.png")
            browser.close()
            sys.exit("Attendance not found.")

        wait()

        if action == "checkin":
            log("Looking for 'Check In' button...")
            try:
                checkin_button = page.get_by_role("button", name="Check In")
                checkin_button.wait_for(timeout=15000)
                if checkin_button.is_visible() and checkin_button.is_enabled():
                    checkin_button.click()
                    log("Check In clicked.")
                else:
                    log("Check In button not visible/enabled.")
                    page.screenshot(path="checkin_not_clickable.png")
            except PlaywrightTimeoutError:
                log("Check In button not found.")
                page.screenshot(path="checkin_not_found.png")

        elif action == "checkout":
            log("Looking for 'Check Out' button...")
            try:
                checkout_button = page.get_by_role("button", name="Check Out")
                checkout_button.wait_for(timeout=15000)
                if checkout_button.is_visible() and checkout_button.is_enabled():
                    checkout_button.click()
                    log("Check Out clicked.")
                else:
                    log("Check Out button not visible/enabled.")
                    page.screenshot(path="checkout_not_clickable.png")
            except PlaywrightTimeoutError:
                log("Check Out button not found.")
                page.screenshot(path="checkout_not_found.png")

        else:
            log(f"Unknown action: {action}")
            browser.close()
            sys.exit(1)

        wait()
        log("Process finished.")
    finally:
        browser.close()

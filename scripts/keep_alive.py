import os
import sys
import time
from playwright.sync_api import sync_playwright

def main():
    url = os.environ.get("STREAMLIT_APP_URL")
    if not url:
        print("Error: STREAMLIT_APP_URL environment variable is not set.")
        print("Please configure this environment variable (or GitHub Action secret) before running.")
        sys.exit(1)

    print(f"Target URL: {url}")
    print("Launching headless Chromium...")
    
    with sync_playwright() as p:
        # Launch headless browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print(f"Navigating to {url}...")
        try:
            # Set a generous navigation timeout of 60 seconds
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            print("Page loaded. Waiting 10 seconds for rendering and initial checks...")
            page.wait_for_timeout(10000)
            
            # Check page title and content
            title = page.title()
            print(f"Loaded page title: '{title}'")
            
            # Look for the wake-up button by text or selectors
            # Streamlit Cloud's sleep screen contains a button with text "Yes, get this app back up!"
            # or it might have specific styling.
            print("Scanning page for Streamlit Cloud hibernation/wake-up elements...")
            
            # Try locating the button using text match
            wakeup_button = page.locator("button:has-text('Yes, get this app back up!')")
            
            # Fallback selectors just in case Streamlit changes their text
            fallback_buttons = [
                page.locator("button:has-text('Wake up')"),
                page.locator("button:has-text('get this app back up')"),
                # Streamlit cloud buttons often have primary classes or structure
                page.locator("button.st-emotion-cache-12t9k85"), # example cached button class
                page.locator("main button")
            ]
            
            clicked = False
            if wakeup_button.count() > 0:
                print("Found standard Streamlit wake-up button! Clicking it...")
                wakeup_button.first.click()
                clicked = True
            else:
                # Check fallbacks
                for fb in fallback_buttons:
                    if fb.count() > 0:
                        text = fb.first.text_content()
                        # Verify we aren't clicking a normal streamlit app button unless it looks like a wake-up button
                        if "wake" in text.lower() or "back up" in text.lower() or "get this" in text.lower():
                            print(f"Found fallback wake-up button with text: '{text}'. Clicking it...")
                            fb.first.click()
                            clicked = True
                            break

            if clicked:
                print("Wake-up button clicked successfully.")
                print("Waiting 45 seconds for Streamlit Community Cloud to rebuild and start the app container...")
                page.wait_for_timeout(45000)
                print("Checking post-wakeup state...")
            else:
                print("No sleep screen or wake-up button detected. The app is likely already awake and running.")

            # Capture screenshot to verify success in the workflow log
            os.makedirs("artifacts", exist_ok=True)
            screenshot_path = "artifacts/keep_alive_status.png"
            page.screenshot(path=screenshot_path)
            print(f"Verification screenshot saved to: {screenshot_path}")
            
            # Verify if the main Streamlit container is visible now
            # Streamlit apps render inside .stApp or within standard containers
            if page.locator(".stApp").count() > 0 or page.locator("[data-testid='stAppViewContainer']").count() > 0:
                print("Success: Streamlit application container detected! App is active.")
            else:
                # Check if it's still loading or has an error
                body_text = page.locator("body").text_content()
                print("Note: Custom container not found in initial DOM. Page text preview:")
                print(body_text[:300].strip().replace('\n', ' | '))

        except Exception as e:
            print(f"An error occurred during keep-alive navigation: {e}")
            # Try to capture screenshot on failure
            try:
                os.makedirs("artifacts", exist_ok=True)
                page.screenshot(path="artifacts/keep_alive_error.png")
                print("Error screenshot saved to artifacts/keep_alive_error.png")
            except Exception as se:
                print(f"Could not save error screenshot: {se}")
            sys.exit(1)
        finally:
            browser.close()
            print("Browser closed. Keep-alive run completed.")

if __name__ == "__main__":
    main()

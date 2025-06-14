import os
import re
from dotenv import load_dotenv
from playwright.sync_api import Page, TimeoutError

def extract_phone_numbers(page: Page) -> list:
    """
    Extracts up to three 10-digit phone numbers from the contact table.
    """
    phone_numbers = []
    try:
        print("Extracting phone numbers from contact table...")
        
        contact_table = page.locator("#DataTables_Table_0")
        contact_table.wait_for(timeout=10000)
        
        links_in_table = contact_table.get_by_role("link").all()
        
        print(f"Found {len(links_in_table)} links in the table to check.")

        for link in links_in_table:
            if len(phone_numbers) >= 3:
                break
            
            number_text = link.inner_text().strip()
            cleaned_number = re.sub(r'[\s\(\)-]', '', number_text)
            
            if re.match(r"^0[0-9]{9}$", cleaned_number):
                phone_numbers.append(cleaned_number)
                print(f"    -> Valid number found: {cleaned_number}")

        print(f"Finished search. Found {len(phone_numbers)} valid phone numbers.")
    except TimeoutError:
        print("Error: Timed out waiting for the contact table to appear.")
    except Exception as e:
        print(f"An error occurred during phone number extraction: {e}")
        
    return phone_numbers


def test_virtual_agent(page: Page, username: str, password: str) -> dict:
    """
    This version navigates directly to the sign-in page and waits for elements to appear.
    """
    result = {"status": "error", "message": "Unknown error", "phone_numbers": []}
    
    try:
        print("Navigating directly to sign-in page...")
        page.goto("https://app.thevirtualagent.co.za/user/sign-in")
        
        print("Waiting for page to load and filling login credentials...")
        page.wait_for_load_state("domcontentloaded")
        
        page.get_by_role("textbox", name="Enter Address").fill(username)
        page.get_by_role("textbox", name="Password").fill(password)
        
        print("Clicking Sign In...")
        page.get_by_role("button", name="Sign In").click()

        # After login, wait for the next page's main element to ensure it has loaded.
        print("Waiting for dashboard to load after login...")
        page.locator("#tab_person_search").wait_for(timeout=30000)

        print("Login successful. Following original 'View Sample' workflow...")
        page.locator("#tab_person_search").get_by_text("View Sample").click()

        print("Selecting sample ID...")
        id_number = "6211141234083"
        
        id_link = page.get_by_role("link", name=id_number)
        
        print(f"Waiting for sample ID link '{id_number}' to be visible...")
        id_link.wait_for(timeout=30000)
        
        print("Link is visible. Clicking now.")
        id_link.click()

        print("Navigating to Contact section...")
        page.get_by_role("link", name=" Contact").click()

        phone_numbers = extract_phone_numbers(page)
        if not phone_numbers:
            result["message"] = "Test completed, but no phone numbers found"
        else:
            result["message"] = "Test automation completed successfully"

        result["status"] = "success"
        result["phone_numbers"] = phone_numbers
        
        return result

    except TimeoutError as e:
        print(f"Error: A step timed out: {str(e)}")
        page.screenshot(path="error_screenshot.png")
        result["message"] = f"Timeout error: {str(e)}"
        return result
    except Exception as e:
        print(f"Error: An unexpected error occurred: {str(e)}")
        page.screenshot(path="error_screenshot.png")
        result["message"] = f"Unexpected error: {str(e)}"
        return result

if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    
    load_dotenv()
    username = os.getenv("VIRTUAL_AGENT_USERNAME")
    password = os.getenv("VIRTUAL_AGENT_PASSWORD")
    
    if not username or not password:
        print("Error: Missing VIRTUAL_AGENT_USERNAME or VIRTUAL_AGENT_PASSWORD in .env file.")
        exit(1)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # --- ANTI-BOT DETECTION SETTINGS ---
        # Create a browser context with human-like properties
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            java_script_enabled=True
        )
        
        # Create the page from our hardened context
        page = context.new_page()
        
        page.set_default_navigation_timeout(60000)
        
        result = test_virtual_agent(page, username, password)
        
        print("\n=== Test Result ===")
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
        print(f"Phone Numbers: {result['phone_numbers']}")
        
        print("\nTest finished. Closing browser.")
        browser.close()
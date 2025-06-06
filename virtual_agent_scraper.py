# virtual_agent_scraper.py
"""
Automates interaction with https://app.thevirtualagent.co.za/user/sign-in using Playwright.
Exports: scrape_phones_for_ids(ids: List[str], username: str, password: str) -> Dict[str, List[str]]
"""
from typing import List, Dict
from playwright.sync_api import sync_playwright
import time

def scrape_phones_for_ids(ids: List[str], username: str, password: str) -> Dict[str, List[str]]:
    """
    For each ID, logs in and scrapes up to 3 cell phone numbers from the Virtual Agent website.
    Returns: {id: [cell1, cell2, ...], ...}
    """
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            # 1. Go to login page
            page.goto("https://app.thevirtualagent.co.za/user/sign-in")
            # 2. Fill in login form (update selectors as needed)
            page.fill('input[name="username"]', username)
            page.fill('input[name="password"]', password)
            page.click('button[type="submit"]')
            page.wait_for_load_state('networkidle')
            # 3. Navigate to correct page (update as needed)
            # Example: page.click('a[href="/search"]')
            # 4. For each ID, fill in field, submit, scrape numbers
            for id_value in ids:
                # Fill in ID field (update selector as needed)
                page.fill('input[name="id"]', id_value)
                page.click('button[type="submit"]')
                page.wait_for_load_state('networkidle')
                # Scrape up to 3 phone numbers (update selector as needed)
                numbers = page.eval_on_selector_all('td.phone', 'nodes => nodes.map(n => n.innerText)')
                results[id_value] = numbers[:3]
                time.sleep(0.5)  # Be polite to the server
            browser.close()
        except Exception as e:
            browser.close()
            raise e
    return results

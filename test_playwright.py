# test_playwright.py — buat file baru ini
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://google.com", timeout=30000, wait_until="domcontentloaded")
    print("URL:", page.url)
    print("Title:", page.title())
    browser.close()
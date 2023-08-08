import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from tqdm import tqdm

from parsing.config import READ_FOLDER, SAVE_FOLDER
from parsing.myio import dump_to_path, load_from_path

langing_page = "https://medium.com/m/signin"
url = "https://medium.datadriveninvestor.com/why-we-use-log-returns-for-stock-returns-820cec4510ba"

# data = load_from_path(READ_FOLDER)

# readpath = Path(READ_FOLDER)
# readfiles = list(readpath.glob("*.json"))
# for f in readfiles:
#     # f = readfiles[1]
#     items = load_from_path(f)
#     print(f"Parsing : {f.name}")
#     saver = []
#     for item in tqdm(items):
#         item = items[100]
#         mid, url = item.get("mediumid"), item.get("medium_url")

# def login():


with sync_playwright() as p:
    # login to medium

    options = {
        "args": [
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--disable-setuid-sandbox",
            "--no-first-run",
            "--no-sandbox",
            "--no-zygote",
            "--ignore-certificate-errors",
            "--disable-extensions",
            "--disable-infobars",
            "--disable-notifications",
            "--disable-popup-blocking",
            "--disable-blink-features=AutomationControlled",
            "--remote-debugging-port=9222",
        ],
        "headless": False,
        "slow_mo": 50,
    }
    browser = p.chromium.launch(**options)
    page = browser.new_page(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    )
    page.goto(langing_page)

    google_button = page.locator("//div[text()='Sign in with Google']")
    google_button.click()

    # time.sleep(5)
    page.wait_for_navigation()
    email_field = page.locator("//input[@type='email']")
    email_field.fill("pan.fessas@gmail.com")
    email_field.press("Enter")

    # time.sleep(5)
    page.wait_for_navigation()
    password_field = page.locator("//input[@type='password']")
    password_field.fill("T28!1990akis")
    password_field.press("Enter")

    # time.sleep(5)
    page.wait_for_navigation()
    page.goto(url)
    page.wait_for_navigation()
    page_content = page.content()
    soup = BeautifulSoup(page_content, "html.parser")

    with open("output.html", "w", encoding="utf-8") as file:
        # Write the prettified HTML to the file
        file.write(soup.prettify())

    browser.close()

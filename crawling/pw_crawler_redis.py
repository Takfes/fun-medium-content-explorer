import json
import time

import redis
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from config import (
    FOLDER_SILVER,
    PW_LANGING_PAGE,
    PW_SLEEP,
    REDIS_HOST,
    REDIS_MAIN_QUEUE,
)
from secretkeys import EMAIL, PASSWORD


def scroll_down():
    page.evaluate("window.scrollTo(0,document.body.scrollHeight);")
    # page.keyboard.press("End")
    # page.mouse.wheel(0, 100_000)


def login(headless=True):
    """login to medium"""
    global browser
    global page

    options = {
        "args": [
            # "--disable-gpu",
            # "--disable-dev-shm-usage",
            # "--disable-setuid-sandbox",
            # "--no-first-run",
            # "--no-sandbox",
            # "--no-zygote",
            # "--ignore-certificate-errors",
            # "--disable-extensions",
            # "--disable-infobars",
            # "--disable-notifications",
            # "--disable-popup-blocking",
            "--disable-blink-features=AutomationControlled",
            # "--remote-debugging-port=9222",
        ],
        "headless": headless,
        "slow_mo": 50,
    }
    # spin up browser
    browser = p.chromium.launch(**options)
    page = browser.new_page(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    )
    page.goto(PW_LANGING_PAGE)
    # select the Google sing in option
    time.sleep(PW_SLEEP)
    google_button = page.locator("//div[text()='Sign in with Google']")
    google_button.click()

    # type in EMAIL
    time.sleep(PW_SLEEP)
    email_field = page.locator("//input[@type='email']")
    email_field.fill(EMAIL)
    email_field.press("Enter")

    # type in PASSWORD
    time.sleep(PW_SLEEP)
    password_field = page.locator("//input[@type='password']")
    password_field.fill(PASSWORD)
    password_field.press("Enter")
    time.sleep(PW_SLEEP * 10)


with sync_playwright() as p:
    # login to medium
    login(headless=False)

    # connect to REDIS
    r = redis.Redis(host=REDIS_HOST, port=6379, db=0)
    print(f"Connected to REDIS")
    # poll REDIS to get url
    counter_jobs = 0

    while True:
        # while counter_jobs <= 100:
        # pop item from REDIS queue
        current_job = r.rpop(REDIS_MAIN_QUEUE)
        if current_job:
            # parse item into dictionary
            current_job = json.loads(current_job)
            # grab url and id
            current_id = current_job.get("id")
            current_url = current_job.get("url")
            print(f"{counter_jobs}) Visiting: {current_id} | {current_url}")

            # Navigate to the page
            # TODO add error handling - if browsing for a page errors, we need to keep track of the failed items and either log them, write them in disk or in a different redis queue
            page.goto(current_url)
            time.sleep(PW_SLEEP)
            # Scroll to the bottom and wait
            scroll_down()
            time.sleep(PW_SLEEP)
            # Grab html content of the page
            page_content = page.content()
            soup = BeautifulSoup(page_content, "html.parser")

            with open(f"{FOLDER_SILVER}/{current_id}.html", "w", encoding="utf-8") as file:
                # Write the prettified HTML to the file
                file.write(soup.prettify())

            counter_jobs += 1
        else:
            print(50 * "=")
            print(f"Visited {counter_jobs} items! Done visiting")
            break

    browser.close()

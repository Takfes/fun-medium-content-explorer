import json
import time

import redis
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from tqdm import tqdm

from parsing.config import SAVE_FOLDER
from parsing.keys import EMAIL, PASSWORD

SLEEP = 5
LANGING_PAGE = "https://medium.com/m/signin"


# def login():
#     """login to medium"""
#     global browser
#     global page

#     options = {
#         "args": [
#             "--disable-gpu",
#             "--disable-dev-shm-usage",
#             "--disable-setuid-sandbox",
#             "--no-first-run",
#             "--no-sandbox",
#             "--no-zygote",
#             "--ignore-certificate-errors",
#             "--disable-extensions",
#             "--disable-infobars",
#             "--disable-notifications",
#             "--disable-popup-blocking",
#             "--disable-blink-features=AutomationControlled",
#             "--remote-debugging-port=9222",
#         ],
#         "headless": False,
#         "slow_mo": 50,
#     }
#     # spin up browser
#     browser = p.chromium.launch(**options)
#     page = browser.new_page(
#         user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
#     )
#     page.goto(LANGING_PAGE)
#     # select the Google sing in option
#     google_button = page.locator("//div[text()='Sign in with Google']")
#     google_button.click()

#     # type in EMAIL
#     # time.sleep(5)
#     email_field = page.locator("//input[@type='email']")
#     email_field.fill(EMAIL)
#     email_field.press("Enter")

#     # type in PASSWORD
#     # time.sleep(5)
#     password_field = page.locator("//input[@type='password']")
#     password_field.fill(PASSWORD)
#     password_field.press("Enter")

#     # time.sleep(5)


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
    # spin up browser
    browser = p.chromium.launch(**options)
    page = browser.new_page(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    )
    page.goto(LANGING_PAGE)
    # select the Google sing in option
    google_button = page.locator("//div[text()='Sign in with Google']")
    google_button.click()

    # type in EMAIL
    time.sleep(5)
    email_field = page.locator("//input[@type='email']")
    email_field.fill(EMAIL)
    email_field.press("Enter")

    # type in PASSWORD
    time.sleep(5)
    password_field = page.locator("//input[@type='password']")
    password_field.fill(PASSWORD)
    password_field.press("Enter")
    time.sleep(5)
    # login()

    # connect to REDIS
    r = redis.Redis(host="localhost", port=6379, db=0)

    # poll REDIS to get url
    counter_jobs = 0

    while counter_jobs <= 10:
        # pop item from REDIS queue
        current_job = r.rpop("queue")
        if current_job:
            # parse item into dictionary
            current_job = json.loads(current_job)
            # grab url and id
            current_id = current_job.get("id")
            current_url = current_job.get("url")
            print(f"Visiting: {current_job.get('url')}")

            # Navigate to the page
            page.goto(current_url)
            time.sleep(5)
            page_content = page.content()
            soup = BeautifulSoup(page_content, "html.parser")

            with open(f"{SAVE_FOLDER}/{current_id}.html", "w", encoding="utf-8") as file:
                # Write the prettified HTML to the file
                file.write(soup.prettify())

            counter_jobs += 1
        else:
            print(50 * "=")
            print(f"Visited {counter_jobs} items! Done visiting")
            break

    browser.close()

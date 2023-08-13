import json
import time

import pika
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from config import (
    FOLDER_SILVER,
    PW_LANGING_PAGE,
    PW_SLEEP,
    RABBITMQ_HOST,
    RABBITMQ_MAIN_QUEUE,
)
from secretkeys import EMAIL, PASSWORD, RABBITMQ_PASS, RABBITMQ_USER


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


def process_job(job, page):
    try:
        # Step: Extract Information from the Job
        current_id = job.get("id")
        current_url = job.get("url")
        print(f"Processing: {current_id} | {current_url}")
        # Step: Navigate to the URL
        page.goto(current_url)
        time.sleep(PW_SLEEP)
        # Step: Scrape Data
        page_content = page.content()
        soup = BeautifulSoup(page_content, "html.parser")
        # Step: Save or Process Data
        with open(f"{FOLDER_SILVER}/{current_id}.html", "w", encoding="utf-8") as file:
            file.write(soup.prettify())
        # Step: Acknowledge Job Completion
        # (This will be handled outside the function, inside the callback function)
    except Exception as e:
        # Step : Handle Errors
        print(f"An error occurred while processing job {current_id}: {e}")
        # (You may choose to requeue the job or handle the error in another way)


def callback(ch, method, properties, body):
    job = json.loads(body)
    success = process_job(job, page)
    if success:
        print(f"Successfully processed job {job['id']}")
        ch.basic_ack(delivery_tag=method.delivery_tag)  # Acknowledge success
    else:
        print(f"Failed to process job {job['id']}. Requeuing...")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)  # Requeue the failed message
    # Check if the queue is empty (stopping criterion)
    queue_status = ch.queue_declare(queue=RABBITMQ_MAIN_QUEUE, passive=True)
    if queue_status.method.message_count == 0:
        print("No more messages in the queue. Exiting.")
        ch.stop_consuming()  # Stop consuming


def main():
    global p
    with sync_playwright() as p:
        # login to medium
        login(headless=False)
        # Define RabbitMQ credentials
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        # Connect to RabbitMQ with credentials
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
        )
        channel = connection.channel()
        # Declare a queue
        queue = channel.queue_declare(queue=RABBITMQ_MAIN_QUEUE)
        # Set up the consumer
        channel.basic_consume(queue=RABBITMQ_MAIN_QUEUE, on_message_callback=callback)
        print("Waiting for messages. To exit press CTRL+C")
        # Start consuming messages
        channel.start_consuming()
        # Close the browser
        browser.close()


if __name__ == "__main__":
    main()

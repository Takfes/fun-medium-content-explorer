from setuptools import setup

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().split("\n")

setup(
    name="chicken",
    version="0.1.1",
    install_requires=requirements,
    py_modules=["scraping", "crawling", "parsing", "config"],
    entry_points={
        "console_scripts": [
            "scrape = scraping.main:default",
        ]
    },
)

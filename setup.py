import re

from setuptools import setup

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [re.sub(r"\s+", "==", x) for x in f.read().split("\n")[2:-1]]

setup(
    name="medium-scrape",
    version="0.0.1",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "scrape = scraping.main:default",
        ]
    },
)

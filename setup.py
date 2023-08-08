from setuptools import setup

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().split("\n")

setup(
    name="myscrapers",
    version="0.0.1",
    install_requires=requirements,
    py_modules=["scraping", "parsing"],
    entry_points={
        "console_scripts": [
            "scrape = scraping.main:default",
        ]
    },
)

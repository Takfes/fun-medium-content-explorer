from pathlib import Path

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from parsing.config import READ_FOLDER, SAVE_FOLDER
from parsing.myio import dump_to_path, load_from_path


def parse_url(url):
    response = requests.get(url)
    response.content
    soup = BeautifulSoup(response.content, "html.parser")
    return {"title": soup.title.text, "content": " ".join([x.text for x in soup.find_all("p")])}


if __name__ == "__main__":
    readpath = Path(READ_FOLDER)
    readfiles = list(readpath.glob("*.json"))
    for f in readfiles:
        # f = readfiles[1]
        items = load_from_path(f)
        print(f"Parsing : {f.name}")
        saver = []
        for item in tqdm(items):
            item = items[100]
            mid, url = item.get("mediumid"), item.get("medium_url")
            content = parse_url(url)
            saver.append({mid: content})
        dump_to_path(saver, f'{SAVE_FOLDER}/{f.name.split("|")[0]}')

        items[13].get("medium_url")

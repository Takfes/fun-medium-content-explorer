from pathlib import Path

from tqdm import tqdm

from parsing.config import READ_FOLDER, SAVE_FOLDER
from parsing.myio import dump_to_path, load_from_path


def parse_url(url):
    pass


if __name__ == "__main__":
    readpath = Path(READ_FOLDER)
    readfiles = list(readpath.glob("*.json"))
    for f in readfiles[1]:
        f = readfiles[1]
        items = load_from_path(f)
        print(f"Parsing : {f.name}")
        saver = []
        for item in tqdm(items[10:15]):
            mid, url = item.get("mediumid"), item.get("medium_url")
            text = parse_url(url)
            saver.append({mid: text})
        dump_to_path(saver, f'{SAVE_FOLDER}/{f.name.split("|")[0]}')

        items[13].get("medium_url")

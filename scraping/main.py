import argparse
import datetime
import json
from pathlib import Path

import requests

from scraping.config import (
    COLLECTIONS,
    DATA_FOLDER,
    REQUEST_LIMIT,
    REQUEST_QUERY,
    REQUEST_URL,
)


def create_payload(catalogid: str, limit: int = REQUEST_LIMIT, offset: int = 0):
    return [
        {
            "operationName": "UserCatalogMainContentQuery",
            "variables": {
                "catalogId": catalogid,
                "pagingOptions": {"limit": limit, "cursor": {"id": "offset:" + str(offset)}},
            },
            "query": REQUEST_QUERY,
        }
    ]


def dump_output(items, name, datapath=DATA_FOLDER):
    timetag = datetime.datetime.now().strftime("%Y%m%d|%H%M%S")
    filepath = Path(f"{datapath}/{name}|{timetag}")
    with open(f"{filepath}.json", mode="w", encoding="utf-8") as f:
        json.dump(items, f)


def parse_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S")


def argument_hanlder():
    parser = argparse.ArgumentParser(description="Medium Reading List Scraper")
    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=REQUEST_LIMIT,
        help=f"An integer representing how many items to to include in each API request, defaults to {REQUEST_LIMIT}",
    )
    parser.add_argument(
        "--collection",
        "-c",
        type=str,
        default=COLLECTIONS["reading_list"],
        help=f"A string representing the medium collection, defaults to 'readilng_list'. Possible values: {','.join(list(COLLECTIONS.keys()))}",
    )
    args = parser.parse_args()
    return args.limit, args.collection


def parse_item(item):
    try:
        parsed = {
            "title": item["entity"]["title"],
            "subtitle": item["entity"]["extendedPreviewContent"]["subtitle"],
            "mediumid": item["entity"]["id"],
            "author": item["entity"]["creator"]["name"],
            "author_followers": item["entity"]["creator"]["socialStats"]["followerCount"],
            "publication_date": parse_timestamp(item["entity"]["firstPublishedAt"]),
            "is_locked": item["entity"]["isLocked"],
            "is_series": item["entity"]["isSeries"],
            "reading_time": item["entity"]["readingTime"],
            "medium_url": item["entity"]["mediumUrl"],
            "claps": item["entity"]["clapCount"],
            "tags": [x.get("id") for x in item["entity"]["tags"]],
            # "collection": item["entity"].get("collection").get("name"),
        }
        return parsed
    except Exception as e:
        pass
        # print(item)


def response_handler(response):
    # parse paging offset - if exists - if it doesn't, this is the last page
    try:
        paging = response[0]["data"]["catalogById"]["itemsConnection"]["paging"]["nextPageCursor"][
            "id"
        ]
        paging_offset = int(paging.replace("offset:", ""))
    except:
        paging_offset = None
    # parse request paging info
    total_item_count = response[0]["data"]["catalogById"]["itemsConnection"]["paging"]["count"]
    return paging_offset, total_item_count


def reponse_parser(response):
    # parse request items
    raw_items = response[0]["data"]["catalogById"]["itemsConnection"]["items"]
    parsed_items = list(map(parse_item, raw_items))
    return parsed_items


def default():
    # determine parameters
    mylimit, mycollection_id = argument_hanlder()
    mycollection = COLLECTIONS[mycollection_id]
    myoffset = 0
    # track requests
    counter = 0
    more_requests = True
    items = []
    # make the requests
    while more_requests:
        # create payload
        request_payload = create_payload(catalogid=mycollection, limit=mylimit, offset=myoffset)
        # make the request
        response = requests.post(REQUEST_URL, json=request_payload)
        resp = response.json()
        items.append(reponse_parser(resp))
        paging_offset, total_item_count = response_handler(resp)
        if paging_offset:
            myoffset = paging_offset
        else:
            more_requests = False
        counter += 1
        print(f"Requests Progress: {counter} requests(s) of {mylimit} out of {total_item_count}")
    # dump output
    dump_output(items, mycollection_id)

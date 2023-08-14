import datetime
from typing import List

import requests

from helpers import configure_logging
from scraping.config import COLLECTIONS, REQUEST_LIMIT, REQUEST_QUERY, REQUEST_URL

LOG_FILE_PATH = "logs/scraper.log"

# Usage
logger = configure_logging(console_output=True, log_to_file=True, log_file_path=LOG_FILE_PATH)


def _create_payload(catalogid: str, limit: int = REQUEST_LIMIT, offset: int = 0):
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


def _parse_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S")


def _parse_item(item):
    try:
        parsed = {"id": item["entity"]["id"], "url": item["entity"]["mediumUrl"]}

        try:
            parsed["title"] = item["entity"]["title"]
        except:
            parsed["title"] = None
        try:
            parsed["subtitle"] = item["entity"]["extendedPreviewContent"]["subtitle"]
        except:
            parsed["subtitle"] = None
        try:
            parsed["author"] = item["entity"]["creator"]["name"]
        except:
            parsed["author"] = None
        try:
            parsed["author_followers"] = item["entity"]["creator"]["socialStats"]["followerCount"]
        except:
            parsed["author_followers"] = None
        try:
            parsed["publication_date"] = _parse_timestamp(item["entity"]["firstPublishedAt"])
        except:
            parsed["publication_date"] = None
        try:
            parsed["reading_time"] = item["entity"]["readingTime"]
        except:
            parsed["reading_time"] = None
        try:
            parsed["claps"] = item["entity"]["clapCount"]
        except:
            parsed["claps"] = None
        try:
            parsed["tags"] = ([x.get("id") for x in item["entity"]["tags"]],)
        except:
            parsed["tags"] = None
        try:
            parsed["is_locked"] = item["entity"]["isLocked"]
        except:
            parsed["is_locked"] = None
        try:
            parsed["collection"] = item["entity"].get("collection").get("name")
        except:
            parsed["collection"] = None
        return parsed
    except Exception as e:
        logger.info(f"{e}")
        logger.info(f"{item}")
        logger.info(50 * "=")


def _response_handler(response):
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


def _response_parser(response):
    # parse request items
    raw_items = response[0]["data"]["catalogById"]["itemsConnection"]["items"]
    parsed_items = list(map(_parse_item, raw_items))
    return parsed_items


def scraper(key: str, limit: int) -> List:
    # determine parameters
    collection_value = COLLECTIONS[key]
    myoffset = 0
    # track requests
    counter = 0
    more_requests = True
    items = []
    # make the requests
    while more_requests:
        # create payload
        request_payload = _create_payload(catalogid=collection_value, limit=limit, offset=myoffset)
        # make the request
        response = requests.post(REQUEST_URL, json=request_payload)
        resp = response.json()
        items.extend(_response_parser(resp))
        paging_offset, total_item_count = _response_handler(resp)
        if paging_offset:
            myoffset = paging_offset
        else:
            more_requests = False
        counter += 1
        print(f"Progress: {key} > request:{counter} | {len(items)}/{total_item_count}")
    return items

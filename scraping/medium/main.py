import datetime

import requests

from scraping.medium.config import (
    COLLECTIONS,
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


def parse_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S")


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


def default(args):
    # determine parameters
    collection_key, limit = args[0], int(args[1])
    collection_value = COLLECTIONS[collection_key]
    myoffset = 0
    # track requests
    counter = 0
    more_requests = True
    items = []
    # make the requests
    while more_requests:
        # create payload
        request_payload = create_payload(catalogid=collection_value, limit=limit, offset=myoffset)
        # make the request
        response = requests.post(REQUEST_URL, json=request_payload)
        resp = response.json()
        items.extend(reponse_parser(resp))
        paging_offset, total_item_count = response_handler(resp)
        if paging_offset:
            myoffset = paging_offset
        else:
            more_requests = False
        counter += 1
        print(f"Progress: {collection_key} > request:{counter} | {len(items)}/{total_item_count}")
    return items

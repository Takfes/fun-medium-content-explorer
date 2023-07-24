import datetime

import requests

from scraping.config import LIBRARY, REQUEST_LIMIT, REQUEST_QUERY, REQUEST_URL


def create_payload(catalogid: str, limit: int = 20, offset: int = 0):
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


def parse_args():
    ...


def parse_item(item):
    return {
        "title": item["entity"]["title"],
        "subtitle": item["entity"]["extendedPreviewContent"]["subtitle"],
        "author": item["entity"]["creator"]["name"],
        "author_followers": item["entity"]["creator"]["socialStats"]["followerCount"],
        "publication_date": item["entity"]["firstPublishedAt"],
        "is_locked": item["entity"]["isLocked"],
        "is_series": item["entity"]["isSeries"],
        "reading_time": item["entity"]["isSeries"],
        "medium_url": item["entity"]["mediumUrl"],
        "claps": item["entity"]["clapCount"],
        "tags": [x.get("id") for x in item["entity"]["tags"]],
        # "collection": item["entity"].get("collection").get("name"),
    }


def parse_response(response):
    # parse request paging info
    next_pate_cursor = response[0]["data"]["catalogById"]["itemsConnection"]["paging"][
        "nextPageCursor"
    ]
    if next_pate_cursor:
        paging = response[0]["data"]["catalogById"]["itemsConnection"]["paging"]["nextPageCursor"][
            "id"
        ]
        paging_offset = int(paging.replace("offset:", ""))
    else:
        paging_offset = None
    total_item_count = response[0]["data"]["catalogById"]["itemsConnection"]["paging"]["count"]

    # parse request items
    raw_items = response[0]["data"]["catalogById"]["itemsConnection"]["items"]
    parsed_items = list(map(parse_item, raw_items))
    return paging_offset, total_item_count, parsed_items


def default():
    # define request parameters
    mylimit = REQUEST_LIMIT
    mylibrary = LIBRARY["ml"]
    myoffset = 0
    total_requests = 0
    all_items = []

    # prepare payload
    request_payload = create_payload(catalogid=mylibrary, limit=mylimit, offset=myoffset)

    # make the request
    response = requests.post(REQUEST_URL, json=request_payload)
    total_requests += 1
    print(f"{total_requests=}")
    # TODO : Request error handling
    resp = response.json()

    # parse response
    paging_offset, total_item_count, parsed_items = parse_response(resp)
    all_items += parsed_items

    # check if more requests are necessary based on total list items and limit
    more_requests = total_item_count > paging_offset

    # while look to make the additional requests
    while more_requests:
        request_payload = create_payload(catalogid=mylibrary, limit=mylimit, offset=paging_offset)
        response = requests.post(REQUEST_URL, json=request_payload)
        total_requests += 1
        print(f"{total_requests=}")
        resp = response.json()
        paging_offset, _, parsed_items = parse_response(resp)
        all_items += parsed_items
        if paging_offset:
            more_requests = total_item_count > paging_offset
        else:
            more_requests = False

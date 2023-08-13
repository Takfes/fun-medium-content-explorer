import requests

CORE_API_KEY = "9YbVlpE41et0jKoUwJLAWFRdIDiNgxGz"
api_endpoint = "https://api.core.ac.uk/v3/"

# ===============================================
# QUERY API - SEARCH WORKS
# ===============================================


def query_api(url_fragment, query, limit=100):
    headers = {"Authorization": "Bearer " + CORE_API_KEY}
    query = {"q": query, "limit": limit}
    response = requests.post(
        f"{api_endpoint}{url_fragment}", data=json.dumps(query), headers=headers
    )
    if response.status_code == 200:
        return response.json(), response.elapsed.total_seconds()
    else:
        print(f"Error code {response.status_code}, {response.content}")
        print(f"Error code {response.status_code}, {response.content}")


query = f"Dispatching concrete trucks using simulation method"

results, elapsed = query_api("search/works", query, limit=1)

results.keys()
results.get("results")
results.get("results")[0]
results.get("results")[0].keys()
results.get("results")[0].get("title")
results.get("results")[0].get("identifiers")

results.get("results")[0].get("abstract")
results.get("results")[0].get("fullText")
results.get("results")[0].get("links")
results.get("results")[0].get("doi")

# ===============================================
#
# ===============================================

limit = 1
url_fragment = "recommend"
searchterm = "Attention is all you need"

headers = {"Authorization": "Bearer " + CORE_API_KEY}

query = {"text": searchterm, "limit": limit}

response = requests.post(f"{api_endpoint}{url_fragment}", data=json.dumps(query), headers=headers)
response.json()

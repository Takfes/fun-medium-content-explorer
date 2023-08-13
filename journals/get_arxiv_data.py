import requests

# Define the search query
query = 'ti:"Attention is all you need"'

# Define the URL for the arXiv search API
url = f"http://export.arxiv.org/api/query?search_query={query}"

# Make the GET request
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    print(response.text)  # Print the raw XML response
else:
    print(f"Error: {response.status_code}")

response.content

# Define the search query
query = 'ti:"Attention is all you need"'

# Define the URL for the arXiv search API
url = f"http://export.arxiv.org/api/query?search_query={query}"

# Make the GET request
response = requests.get(url)
response.text

from typing import List

from pymongo import DESCENDING, MongoClient

client = MongoClient("localhost", 27017)
db = client["db"]
collection = db["my_collection"]

# ===============================================
# Manipulate indices
# ===============================================

# list indexes
indexes = collection.list_indexes()
for index in indexes:
    print(index["name"])

# Create index
collection.create_index(
    [("title", "text"), ("subtitle", "text"), ("text", "text")], name="multitext_index"
)

collection.create_index([("title", "text")], name="title_index")

# Drop an index by its name
collection.drop_index("multitext_index")
collection.drop_index("title_index")

# ===============================================
# Search Text
# ===============================================


def mngdb_search_text(searchterm: str, whole_string: bool = False, limit: int = 100) -> List:
    if whole_string:
        searchterm = '\"' + searchterm + '\"'
    # Define the search query
    query = {"$text": {"$search": searchterm}}
    score = {"score": {"$meta": "textScore"}}
    # Execute the query and sort by claps in descending order
    result = (
        collection.find(query, projection=score)
        .sort([("score", {"$meta": "textScore"})])
        .limit(limit)
    )
    return [x for x in result]

results = mngdb_search_text("operations research", True)

for i, item in enumerate(results, start=1):
    print(
        f"{i}) {item['title']} ⏰ {item['reading_time']:.1f} 👏 {item['claps']} \n 🏷 {item['tags']}\n"
    )

# ===============================================
# My queries - Top Claps Articles
# ===============================================

# Find the top 5 documents sorted by the "claps" field in descending order
top_documents = collection.find().sort("claps", DESCENDING).limit(10)

# Print the results
for i, document in enumerate(top_documents):
    print(f'{i}) {document["claps"]} - {document["title"]}')

# ===============================================
# My queries - Author Stats
# ===============================================

# Define the aggregation pipeline
pipeline = [
    {
        "$group": {
            "_id": "$author",
            "count": {"$sum": 1},
            "average_claps": {"$avg": "$claps"},
            "max_claps": {"$max": "$claps"},
        }
    },
    {"$match": {"count": {"$gt": 5}}},
    {"$sort": {"count": -1}},
]

# Execute the aggregation
result = collection.aggregate(pipeline)

# Print the results
for author_stats in result:
    print(
        f"Author: {author_stats['_id']}, Count: {author_stats['count']}, Average Claps: {author_stats['average_claps']}, Max Claps: {author_stats['max_claps']}"
    )

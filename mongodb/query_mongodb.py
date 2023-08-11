from pymongo import DESCENDING, MongoClient

client = MongoClient("localhost", 27017)
db = client["my_database"]
collection = db["my_collection"]

# ===============================================
# Manipulate indices
# ===============================================

# create
collection.create_index(
    [("title", "text"), ("subtitle", "text"), ("text", "text")], name="multitext_index"
)

collection.create_index([("title", "text")], name="title_index")

indexes = collection.list_indexes()
for index in indexes:
    print(index["name"])

# Drop an index by its name
collection.drop_index("text_fields_index")
collection.drop_index("title_index")

# ===============================================
# Search based on title
# ===============================================

query = {"$text": {"$search": "transformers"}}

result = collection.find(query).sort("claps", -1)

for i, document in enumerate(result):
    print(f'{i}) {document["claps"]} - {document["title"]}')

# ===============================================
# Search Articles
# ===============================================

# Define the search query
query = {"$text": {"$search": "transformers"}}

# Execute the query and sort by claps in descending order
result = collection.find(query).sort("claps", -1)

# Print the results
for i, document in enumerate(result):
    print(f'{i}) {document["claps"]} - {document["title"]}')

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

# ===============================================
# Generic Queries
# ===============================================

# Find documents where the 'name' field contains 'Alice' or 'Bob'
results = collection.find({"name": {"$regex": "Alice|Bob"}})
for result in results:
    print(result)

# Find documents where the 'name' field is 5 characters long
results = collection.find({"$where": "this.name.length == 5"})
for result in results:
    print(result)

# Find documents where the 'name' field starts with 'Al'
results = collection.find({"name": {"$regex": "^Al"}})
for result in results:
    print(result)

# Find documents where the 'name' field ends with 'e'
results = collection.find({"name": {"$regex": "e$"}})
for result in results:
    print(result)

# Find documents where the 'name' field contains 'alice', case-insensitive
results = collection.find({"name": {"$regex": "alice", "$options": "i"}})
for result in results:
    print(result)

# Find results based on numeric field query
results = collection.find({"age": 30})
for result in results:
    print(result)

results = collection.find({"age": {"$gt": 25}})
for result in results:
    print(result)

# Search text
results = collection.find({"$text": {"$search": "search_term"}})
for result in results:
    print(result)

# Create a text index with weights
collection.create_index(
    [("name", "text"), ("description", "text")], weights={"name": 10, "description": 2}
)

db.drop_collection("my_collection")

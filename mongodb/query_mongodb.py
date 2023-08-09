from pymongo import MongoClient

client = MongoClient("localhost", 27017)
db = client["my_database"]
collection = db["my_collection"]

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

# Create a text index with weights
collection.create_index(
    [("name", "text"), ("description", "text")], weights={"name": 10, "description": 2}
)

# Search text
results = collection.find({"$text": {"$search": "search_term"}})
for result in results:
    print(result)

from pymongo import MongoClient

client = MongoClient("localhost", 27017)
db = client["my_database"]
collection = db["my_collection"]

documents = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
    {"name": "Charlie", "age": 35},
]

collection.insert_many(documents)

results = collection.find({"age": 30})
for result in results:
    print(result)

results = collection.find({"age": {"$gt": 25}})
for result in results:
    print(result)

db.drop_collection("my_collection")

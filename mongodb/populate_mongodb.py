import pickle

from pymongo import MongoClient

from config import FOLDER_GOLD, MONGO_COLLECTION, MONGO_DB, MONGO_HOST

# ===============================================
# Connect to Mongodb
# ==============================================
client = MongoClient(MONGO_HOST, 27017)

# List all databases
dbs = client.list_database_names()
for i, db_name in enumerate(dbs, start=1):
    print(f"{i}) Database : {db_name}")
    # List all collections in a database
    db = client[db_name]
    collections = db.list_collection_names()
    for j, collection_name in enumerate(collections, start=1):
        print(f"  {j}) Collection : {db_name}.{collection_name}")

# # Delete a database named "mydatabase"
# client.drop_database("mydatabase")

# # Delete a collection
# db = client["db"]
# collection = db["my_collection"]
# collection.drop()
# # Delete a collection
# db.drop_collection("my_collection")

db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

# ===============================================
# Read data
# ===============================================
with open(f"{FOLDER_GOLD}/master.pickle", "rb") as f:
    master = pickle.load(f)

documents = list(master.values())

# ===============================================
# Push documents to MongoDB
# ===============================================
collection.insert_many(documents)

# Get the count of documents in the collection
count = collection.count_documents({})

# Validate document count is what expected
assert len(documents) == count

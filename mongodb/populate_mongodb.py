import pickle

from pymongo import MongoClient

from config import FOLDER_GOLD, MONGO_COLLECTION, MONGO_DB, MONGO_HOST

# ===============================================
# Connect to Mongodb
# ==============================================

client = MongoClient(MONGO_HOST, 27017)

# Check if connection is successful
# print(client.server_info())

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

# ===============================================
# Manipulate indices
# ===============================================

# list indexes
indexes = collection.list_indexes()
# check if index exists
if not "multitext_index" in [index["name"] for index in indexes]:
    print("Index does not exist")
    # create index
    collection.create_index(
        [("title", "text"), ("subtitle", "text"), ("text", "text")], name="multitext_index"
    )
else:
    print("Index already exists")

# Drop an index by its name
# collection.drop_index("multitext_index")

# Close connection
client.close()

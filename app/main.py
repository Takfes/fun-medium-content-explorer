from typing import List

import streamlit as st
from pymongo import MongoClient

# ===============================================
# Function Definitions
# ===============================================


def connect_mongodb():
    client = MongoClient("localhost", 27017)
    db = client["db"]
    return db["my_collection"]


@st.cache_data()
def mongo_search_text(searchterm: str, whole_string: bool = False, limit: int = 100) -> List:
    if whole_string:
        searchterm = '"' + searchterm + '"'
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


# ===============================================
# Main Streamlit App
# ===============================================

# Initialize session state variables
if "results" not in st.session_state:
    st.session_state.results = []

collection = connect_mongodb()
st.header("Search Articles")

# Input for search term
searchterm = st.text_input(label="Enter search terms")

# Check if the search term is not empty
if searchterm:
    # Check if the search term has changed
    if "searchterm" not in st.session_state or st.session_state.searchterm != searchterm:
        st.session_state.searchterm = searchterm
        st.session_state.results = mongo_search_text(searchterm)

    # Display the results
    for i, item in enumerate(st.session_state.results, start=1):
        st.write(
            f"{i}) {item['title']} ⏰ {item['reading_time']:.1f} 👏 {item['claps']} \n 🏷 {item['tags']}\n"
        )
else:
    st.write("Enter a search term to see results.")

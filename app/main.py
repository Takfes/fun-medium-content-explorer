import datetime
from typing import List

import streamlit as st
from pymongo import MongoClient

from config import MONGO_COLLECTION, MONGO_DB, MONGO_HOST

# ===============================================
# Function Definitions
# ===============================================


def connect_mongodb():
    client = MongoClient(MONGO_HOST, 27017)
    db = client[MONGO_DB]
    return db[MONGO_COLLECTION]


@st.cache_data()
def mongo_search(searchterm: str, filters: dict, limit: int = 100) -> List:
    # Check if whole_string is set in filters
    if filters.get("whole_string"):
        searchterm = '"' + searchterm + '"'
    # Define the base search query
    query = {"$text": {"$search": searchterm}}
    score = {"score": {"$meta": "textScore"}}

    # Apply reading time filter
    if "reading_time" in filters:
        reading_time_min, reading_time_max = filters["reading_time"]
        query["reading_time"] = {"$gte": reading_time_min, "$lte": reading_time_max}

    # Apply date filter
    if "minimum_date" in filters:
        query["publication_date"] = {"$gte": filters["minimum_date"]}

    # Apply claps filter
    if "claps_limits" in filters:
        claps_min = filters["claps_limits"]
        query["claps"] = {"$gte": claps_min}

    # Modify the result limit if set in filters
    if "results_limit" in filters:
        limit = filters["results_limit"]

    # Execute the query and sort by text score in descending order
    result = (
        collection.find(query, projection=score)
        .sort([("score", {"$meta": "textScore"})])
        .limit(limit)
    )

    return [x for x in result]


def render_sidebar():
    filters = {}
    # Enable result limits
    if st.sidebar.checkbox("📏 Enable result limits"):
        filters["results_limit"] = st.sidebar.slider(
            label="Select range for results to show",
            min_value=5,
            max_value=250,
            value=10,
        )
    # Reading time filter
    if st.sidebar.checkbox("⏰ Enable reading time filter"):
        filters["reading_time"] = st.sidebar.slider(
            label="Select range for reading time",
            min_value=0,
            max_value=90,
            value=(5, 20),
        )
    # Date filter - applies to publication date
    if st.sidebar.checkbox("🗓 Enable minimum publication date filter"):
        default_date = datetime.datetime(2020, 1, 1)
        min_date = datetime.datetime(2015, 1, 1)
        minimum_date = st.sidebar.date_input(
            "Select a date range:",
            min_value=min_date,
            value=default_date,
        )
        filters["minimum_date"] = minimum_date.strftime("%Y-%m-%d")
    # Search term match - partial or full
    filters["whole_string"] = st.sidebar.checkbox("🎚 Search term full match")
    # Claps filter
    if st.sidebar.checkbox("👏 Enable claps filter"):
        filters["claps_limits"] = st.sidebar.slider(
            label="Select minimum # of claps", min_value=0, max_value=1000, value=100
        )
    return filters


def html_component(thumbnail, title, url, author, claps, reading_time, tags, publication_date):
    tags_html = ", ".join(tags[:3])
    html = f"""
    <div class="result-box">
        <div class="image-container">
            <a href="{url}" target="_blank">
                <img src="{thumbnail}" alt="{title}" class="thumbnail">
            </a>
        </div>
        <div class="content-container">
            <a href="{url}" target="_blank" class="title">{title}</a>
            <div class="author-tags">
                <span class="author">By {author}</span> &middot;
                <span class="tags">{tags_html}</span>
            </div>
            <div class="claps-reading">
                <span class="claps">👏 {claps}</span> &middot;
                <span class="reading-time">⏰ {reading_time:.1f} min</span> &middot;
                <span class="publication-date">🗓 {publication_date}</span>
            </div>
        </div>
    </div>
    """
    return html


def load_css(file_name):
    with open(file_name) as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


load_css("app/styles.css")

# ===============================================
# Main Streamlit App
# ===============================================

# Initialize session state variables
if "results" not in st.session_state:
    st.session_state.results = []

search_filters = render_sidebar()
collection = connect_mongodb()
st.header("Search Articles")

# Input for search term
searchterm = st.text_input(label="Enter search terms")

# Check if the search term is not empty
if searchterm:
    # Check if the search term has changed
    if "searchterm" not in st.session_state or st.session_state.searchterm != searchterm:
        st.session_state.searchterm = searchterm
        st.session_state.results = mongo_search(searchterm, filters=search_filters)

    # Display the results

    # for i, item in enumerate(st.session_state.results, start=1):
    #     st.write(
    #         f"{i}) {item['title']} ⏰ {item['reading_time']:.1f} 👏 {item['claps']} \n 🏷 {item['tags']}\n"
    #     )

    for item in st.session_state.results:
        html = html_component(
            thumbnail=item["top_image"],
            title=item["title"],
            url=item["medium_url"],
            author=item["author"],
            claps=item["claps"],
            reading_time=item["reading_time"],
            publication_date=item["publication_date"],
            tags=item["tags"],
        )
        st.markdown(html, unsafe_allow_html=True)

else:
    st.write("Enter a search term to see results.")

import datetime
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
def mongo_search(searchterm: str, whole_string: bool = False, limit: int = 100) -> List:
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


def render_sidebar():
    filters = {}
    # Enable result limits
    if st.sidebar.checkbox("📏 Enable result limits"):
        filters["results_limit"] = st.sidebar.slider(
            label="Select range for results to show",
            min_value=5,
            max_value=1_000,
            value=20,
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
    if st.sidebar.checkbox("🗓 Enable date filter"):
        min_date = datetime.datetime(2015, 1, 1)
        max_date = datetime.datetime(2023, 12, 31)
        start_date, end_date = st.sidebar.date_input(
            "Select a date range:",
            min_value=min_date,
            max_value=max_date,
            value=(min_date, max_date),
        )
        filters["start_date"] = start_date.strftime("%Y-%m-%d")
        filters["end_date"] = end_date.strftime("%Y-%m-%d")
    # Search term match - partial or full
    filters["whole_string"] = st.sidebar.checkbox("🎚 Search term full match")
    # Claps filter
    if st.sidebar.checkbox("👏 Enable claps filter"):
        filters["claps_limits"] = st.sidebar.slider(
            label="Select range for claps", min_value=0, max_value=30_000, value=(100, 1_000)
        )
    return filters


def html_component(thumbnail, title, url, author, claps, reading_time, tags):
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
                <span class="reading-time">⏰ {reading_time:.1f} min</span>
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

render_sidebar()
collection = connect_mongodb()
st.header("Search Articles")

# Input for search term
searchterm = st.text_input(label="Enter search terms")

# Check if the search term is not empty
if searchterm:
    # Check if the search term has changed
    if "searchterm" not in st.session_state or st.session_state.searchterm != searchterm:
        st.session_state.searchterm = searchterm
        st.session_state.results = mongo_search(searchterm)

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
            tags=item["tags"],
        )
        st.markdown(html, unsafe_allow_html=True)

else:
    st.write("Enter a search term to see results.")

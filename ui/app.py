import streamlit as st
import pandas as pd
import sys
import os

current_file_dir = os.path.dirname(os.path.abspath(__file__)) 
project_root = os.path.dirname(current_file_dir) 
core_path = os.path.join(project_root, 'core')
data_path = os.path.join(project_root, 'data') 

if core_path not in sys.path:
    sys.path.append(core_path)

from query_engine import QueryEngine 
from storage import Storage

DATA_FILE_PATH = os.path.join(data_path, "dataset.csv") 

@st.cache_resource(show_spinner=True)
def initialize_db(path):
    st.info("Initializing MiniDB: Loading data and building AVL/Social Graph...")
    storage_instance = Storage(path)
    storage_instance.initialize() 
    engine = QueryEngine(storage_instance)
    st.success(f"MiniDB loaded successfully with {len(engine.storage.hash_map):,} records.")
    return engine

def run_app():
    st.set_page_config(layout="wide")
    st.title("DS & Algo/Group 7 - Social Network Analytics")
    st.markdown("Implemented with **AVL Trees** for indexing and **Graph Algorithms** for social connections.")
    
    db = initialize_db(DATA_FILE_PATH)

    st.sidebar.header("Operations")
    operation = st.sidebar.selectbox("Select MiniDB Feature", 
                                     ["Indexed Search & Performance", 
                                      "Social Graph Analytics",
                                      "Descriptive Analytics"])

    if operation == "Indexed Search & Performance":
        st.header("AVL Tree Indexing Demo")
        
        st.subheader("1. Point Query: Search by User ID (O(1) Lookup)")
        col1, col2 = st.columns([1, 4])
        with col1:
            search_id = st.number_input("Enter User ID", min_value=1, step=1, key='search_id')
        with col2:
            st.markdown("---") 
            
        if st.button("Search Record"):
            record = db.get_record_by_id(search_id)
            if record:
                st.dataframe(pd.DataFrame([record]))
            else:
                st.warning(f"User ID {search_id} not found.")

        st.markdown("---")

        st.subheader("2. Range Query: Age Range (O(log N + K) AVL Index)")
        col1, col2 = st.columns(2)
        with col1:
            min_age = st.slider("Minimum Age", 18, 100, 20)
        with col2:
            max_age = st.slider("Maximum Age", 18, 100, 30)
        
        if st.button("Run Performance Comparison"):
            st.text("Executing queries and comparing timing (check terminal for console output)...")
            results = db.compare_linear_search_by_age_range(min_age, max_age)
            
            st.write(f"Found {len(results)} users between ages {min_age} and {max_age}:")
            if results:
                st.dataframe(pd.DataFrame(results))
            else:
                st.info("No records found in this range.")

    elif operation == "Social Graph Analytics":
        st.header("Graph Algorithm Demo (BFS)")

        st.subheader("1. Find Shortest Connection (Degrees of Separation)")
        col1, col2 = st.columns(2)
        with col1:
            user_a = st.number_input("User A ID", min_value=1, step=1, key='user_a')
        with col2:
            user_b = st.number_input("User B ID", min_value=1, step=1, key='user_b')
        
        if st.button("Trace Connection"):
            path_records = db.find_shortest_path(user_a, user_b)
            if path_records:
                path_str = " -> ".join([f"{r['user_id']}" for r in path_records])
                st.success(f"Connection found! Distance: {len(path_records) - 1}")
                st.code(path_str)
                st.dataframe(pd.DataFrame(path_records))
            else:
                st.warning(f"No connection found between {user_a} and {user_b}.")

        st.markdown("---")
        
        st.subheader("2. Show User Friends")
        target_id = st.number_input("Enter User ID to see friends", min_value=1, step=1, key='friend_target')
        if st.button("Get Friends"):
            friends = db.get_user_friends(target_id)
            if friends:
                st.write(f"Found {len(friends)} friends:")
                st.dataframe(pd.DataFrame(friends))
            else:
                st.info(f"User ID {target_id} has no friends listed (or user not found).")
            
    elif operation == "Descriptive Analytics":
        st.header("Basic Data Analysis")
        
        st.subheader("1. Value Distribution (Categorical Fields)")
        # LANGUAGES ADDED HERE
        cat_attributes = ["gender", "eye_color", "education", "languages", "music"] 
        dist_attr = st.selectbox("Select Attribute", cat_attributes, key='dist_attr')
        if st.button("Show Distribution"):
            # If the user selects "languages", we can directly call the storage method for efficiency.
            if dist_attr == "languages":
                 distribution_list = db.storage.top_languages(top_k=50) # Use top_k=50 for a reasonable display
                 distribution = dict(distribution_list)
            else:
                distribution = db.get_distribution(dist_attr)
            
            if distribution:
                df_dist = pd.DataFrame(distribution.items(), columns=[dist_attr, 'Count']).sort_values(by='Count', ascending=False)
                st.dataframe(df_dist)
                st.bar_chart(df_dist.set_index(dist_attr))
            else:
                st.warning(f"No data found for attribute {dist_attr}.")

if __name__ == "__main__":
    run_app()
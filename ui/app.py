import streamlit as st
import pandas as pd
import time
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, os.pardir))
core_path = os.path.join(project_root, 'core')
data_path = os.path.join(project_root, 'data')

if core_path not in sys.path:
    sys.path.append(core_path)

from query_engine import QueryEngine 
from storage import Storage

DATA_FILE_PATH = os.path.join(data_path, "dataset.csv") 

@st.cache_resource(show_spinner=True)
def initialize_db(path):
    st.info("Initializing MiniDB: Loading data and building AVL/Graph structures...")
    storage_instance = Storage(path)
    storage_instance.initialize() 
    engine = QueryEngine(storage_instance)
    st.success(f"MiniDB loaded successfully with {len(engine.storage.hash_map):,} records.")
    return engine

def run_app():
    st.set_page_config(layout="wide")
    st.title("DS & Algo/Group 7 - Scalable Data Management System")
    st.markdown("Implemented with **AVL Trees** for indexing and **Graph Algorithms** for relationships.")
    
    db = initialize_db(DATA_FILE_PATH)

    st.sidebar.header("Operations")
    operation = st.sidebar.selectbox("Select MiniDB Feature", 
                                     ["Indexed Search & Performance", 
                                      "Graph Analytics (Hierarchy)",
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

    elif operation == "Graph Analytics (Hierarchy)":
        st.header("Graph Algorithm Demo (BFS)")

        st.subheader("1. Find Path to CEO (Upward Traversal)")
        user_id_path = st.number_input("Enter User ID to find hierarchy path:", min_value=1, step=1, key='user_path')
        
        if st.button("Trace Path"):
            path_records = db.find_shortest_path_to_ceo(user_id_path)
            if path_records:
                path_str = " -> ".join([f"{r['user_id']} ({r.get('education', 'N/A')})" for r in path_records])
                st.success(f"Path Length: {len(path_records) - 1}")
                st.code(path_str)
                st.dataframe(pd.DataFrame(path_records))
            else:
                st.warning(f"User ID {user_id_path} not found or path cannot be traced.")

        st.markdown("---")
        
        st.subheader("2. Compound Query: Direct Reports")
        manager_id = st.number_input("Enter Manager ID", min_value=0, step=1, key='manager_id')
        if st.button("Get Direct Reports"):
            report_ids = db.storage.get_direct_reports(manager_id)
            report_data = db.storage.get_all_records(report_ids)
            if report_data:
                st.write(f"Found {len(report_data)} direct reports:")
                st.dataframe(pd.DataFrame(report_data))
            else:
                st.info(f"Manager ID {manager_id} has no direct reports (or is not found).")
            
    elif operation == "Descriptive Analytics":
        st.header("Basic Data Analysis")
        
        st.subheader("1. Descriptive Statistics (Numerical Fields)")
        num_attributes = ["age"] 
        stats_attr = st.selectbox("Select Attribute", num_attributes, key='stats_attr')
        if st.button("Calculate Statistics"):
            stats = db.get_descriptive_statistics(stats_attr)
            st.json(stats)
            
        st.markdown("---")
        
        st.subheader("2. Value Distribution (Categorical Fields)")
        cat_attributes = ["gender", "eye_color", "education", "languages", "music"] 
        dist_attr = st.selectbox("Select Attribute", cat_attributes, key='dist_attr')
        if st.button("Show Distribution"):
            distribution = db.get_distribution(dist_attr)
            
            if distribution:
                df_dist = pd.DataFrame(distribution.items(), columns=[dist_attr, 'Count']).sort_values(by='Count', ascending=False)
                st.dataframe(df_dist)
                st.bar_chart(df_dist.set_index(dist_attr))
            else:
                st.warning(f"No data found for attribute {dist_attr}.")

run_app()
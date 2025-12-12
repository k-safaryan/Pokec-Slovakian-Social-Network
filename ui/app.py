import streamlit as st
import os
import sys
import pandas as pd
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, os.pardir))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from core.storage import Storage
    from core.query_engine import QueryEngine
except ImportError:
    st.error("FATAL: Could not import core modules. Check the project structure.")
    sys.exit()
except ModuleNotFoundError as e:
    st.error(f"FATAL: Missing Python module. Did you run 'pip install pandas' and 'pip install streamlit'? Error: {e}")
    sys.exit()

DATA_FILE = 'dataset.csv'
DATA_PATH = os.path.join(project_root, 'data', DATA_FILE) 

@st.cache_resource
def load_data_and_engine():
    st.info("Loading 1.6M records and building AVL/Graph indices. This will take several minutes and runs only once.")
    try:
        storage = Storage(DATA_PATH)
        start_time = time.time()
        storage.initialize()
        end_time = time.time()
        engine = QueryEngine(storage)
        
        st.success(f"Database loaded successfully! (Time taken: {end_time - start_time:.2f} seconds)")
        return storage, engine
    except Exception as e:
        st.error(f"Error during initialization: {e}")
        return None, None

st.set_page_config(layout="wide", page_title="MiniDB: Pokec Social Network")

st.title("DS115 MiniDB: Pokec Network Management System")

storage, engine = load_data_and_engine()

if storage and engine:
    
    st.header("1. Indexed Search (AVL Tree)")
    st.markdown("Querying the **Age** index for efficient $\\mathcal{O}(\\log N + K)$ range searches.")

    col1, col2, col3 = st.columns(3)
    min_age = col1.number_input("Minimum Age", min_value=15, max_value=112, value=18)
    max_age = col2.number_input("Maximum Age", min_value=15, max_value=112, value=25)
    limit = col3.number_input("Results Limit", min_value=1, max_value=100, value=10)

    if st.button("Run Indexed Range Search"):
        if min_age > max_age:
            st.warning("Minimum Age must be less than Maximum Age.")
        else:
            start_query = time.perf_counter()
            results = engine.search_by_index_score(min_age, max_age)
            end_query = time.perf_counter()
            
            st.success(f"Found {len(results):,} records in {((end_query - start_query) * 1000):.3f} ms.")
            
            if results:
                st.subheader(f"Top {limit} Results:")
                st.dataframe(pd.DataFrame(results[:limit]), use_container_width=True)


    st.markdown("---")
    
    st.header("2. Graph Traversal (Path to Root)")
    st.markdown("Demonstrates pathfinding from any node up to the ultimate network Root.")

    user_id_input = st.number_input("Enter User ID for Path to Root (e.g., 1, 2, or 5):", value=2, step=1)
    
    if st.button("Find Path to Root"):
        start_graph = time.perf_counter()
        path_records = engine.find_shortest_path_to_ceo(user_id_input)
        end_graph = time.perf_counter()
        
        if path_records:
            path_ids = [record['user_id'] for record in path_records]
            st.success(f"Path Found (Length: {len(path_ids)-1}, Time: {((end_graph - start_graph) * 1000):.3f} ms):")
            st.code(" -> ".join(map(str, path_ids)))
            st.dataframe(pd.DataFrame(path_records), use_container_width=True)
        else:
            st.warning(f"Path not found for user ID {user_id_input}. ID may be the root or an isolated node.")

    st.markdown("---")
    
    st.header("3. Basic Analytics (Data Distribution)")
    
    attribute = st.selectbox("Select Attribute for Distribution:", 
                             ['gender', 'eye_color', 'education', 'languages', 'music'])
    
    if st.button("Calculate Distribution"):
        distribution = engine.get_distribution(attribute)
        
        if distribution:
            dist_df = pd.DataFrame(distribution.items(), columns=['Value', 'Count']).sort_values('Count', ascending=False).head(10)
            
            st.success(f"Top 10 Distribution for '{attribute}':")
            
            st.bar_chart(dist_df, x='Value', y='Count')
            st.dataframe(dist_df, use_container_width=True)

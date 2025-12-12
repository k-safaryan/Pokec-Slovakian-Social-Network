import streamlit as st
import pandas as pd
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, '..')
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
from core.storage import Storage
from core.query_engine import QueryEngine

DATA_FILE = 'dataset.csv'
RELATIONSHIP_FILE = 'relationships.csv'
DATA_PATH = os.path.join(project_root, 'data', DATA_FILE)
RELATIONSHIP_PATH = os.path.join(project_root, 'data', RELATIONSHIP_FILE)


@st.cache_resource(show_spinner="Initializing Database and Building Indexes (This may take a minute...)")
def initialize_db(data_path: str, relationship_path: str) -> Storage:
    storage_instance = Storage(data_path, relationship_path)
    storage_instance.initialize()
    return storage_instance

def run_app():
    st.set_page_config(layout="wide", page_title="Pokec Social Network Analysis")

    storage_instance = initialize_db(DATA_PATH, RELATIONSHIP_PATH)
    query_engine = QueryEngine(storage_instance)

    st.title("Pokec Social Network Analysis")

    # --- Sidebar for Navigation ---
    analysis_type = st.sidebar.radio(
        "Select Analysis Type",
        ["Descriptive Analytics", "Search & Retrieval", "Graph Analytics"]
    )

    if analysis_type == "Descriptive Analytics":
        st.header("Descriptive Analytics")
        st.markdown("Overview of the dataset distribution.")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Gender Distribution")
            gender_data = query_engine.storage.count_by_gender()
            gender_df = pd.DataFrame(list(gender_data.items()), columns=['Gender', 'Count'])
            st.bar_chart(gender_df.set_index('Gender'))
            
            st.subheader("Education Distribution (Top 10)")
            education_data = query_engine.storage.top_educations(10)
            education_df = pd.DataFrame(education_data, columns=['Education', 'Count'])
            st.dataframe(education_df, use_container_width=True)

        with col2:
            st.subheader("Average Age by Gender")
            age_data = query_engine.storage.average_age_by_gender()
            age_df = pd.DataFrame(list(age_data.items()), columns=['Gender', 'Average Age'])
            st.bar_chart(age_df.set_index('Gender'))

            st.subheader("Language Distribution (Top 10)")
            language_data = query_engine.storage.top_languages(10)
            language_df = pd.DataFrame(language_data, columns=['Language', 'Count'])
            st.dataframe(language_df, use_container_width=True)

        st.subheader("Network Metrics")
        avg_friends = query_engine.storage.average_number_of_friends()
        med_friends = query_engine.storage.median_number_of_friends()
        
        st.write(f"**Average Number of Friends:** {avg_friends:.2f}")
        st.write(f"**Median Number of Friends:** {med_friends:.2f}")

        st.subheader("Degree Distribution (Top 10 Most Connected)")
        most_connected = query_engine.storage.top_k_most_connected(10)
        conn_df = pd.DataFrame(most_connected, columns=['User ID', 'Connections'])
        st.dataframe(conn_df, use_container_width=True)


    elif analysis_type == "Search & Retrieval":
        st.header("Indexed Search & Retrieval")

        tab1, tab2 = st.tabs(["Search by User ID (O(1))", "Search by Age Range (O(log N))"])

        with tab1:
            st.subheader("Lookup User by ID (Hash Map)")
            user_id = st.number_input("Enter User ID", min_value=1, value=1, step=1)
            
            if st.button("Search User"):
                user_record = query_engine.get_record_by_id(user_id)
                if user_record:
                    st.dataframe(pd.DataFrame([user_record]), use_container_width=True)
                else:
                    st.warning(f"User ID {user_id} not found.")

        with tab2:
            st.subheader("Search by Age Range (AVL Tree Index)")
            col_min, col_max = st.columns(2)
            with col_min:
                min_age = st.number_input("Minimum Age", min_value=1, value=18, step=1)
            with col_max:
                max_age = st.number_input("Maximum Age", min_value=1, value=25, step=1)
                
            if st.button("Search Age Range"):
                results, time_indexed = query_engine.search_by_index_score(min_age, max_age, return_time=True)
                
                st.info(f"Indexed search found {len(results):,} records in {time_indexed:.6f} seconds.")
                
                if results:
                    df = pd.DataFrame(results)
                    st.dataframe(df.head(100), use_container_width=True)
                    if len(results) > 100:
                        st.write(f"Displaying the first 100 of {len(results):,} results.")

    elif analysis_type == "Graph Analytics":
        st.header("Social Graph Analytics")

        st.subheader("Shortest Path (Degrees of Separation)")
        col_start, col_end = st.columns(2)
        with col_start:
            start_id = st.number_input("Source User ID (A)", min_value=1, value=1, step=1)
        with col_end:
            end_id = st.number_input("Target User ID (B)", min_value=1, value=100, step=1)

        if st.button("Find Path"):
            path_ids, time_path = query_engine.find_shortest_path_timed(start_id, end_id)

            if path_ids:
                st.success(f"Path found in {time_path:.6f} seconds. Length: {len(path_ids) - 1} connections.")
                
                path_records = storage_instance.get_all_records(path_ids)
                df = pd.DataFrame(path_records)
                df['Path Step'] = range(len(df))
                
                st.dataframe(df[['Path Step', 'user_id', 'gender', 'age', 'education']], use_container_width=True)
            else:
                st.warning(f"No path found between User {start_id} and User {end_id}.")

run_app()
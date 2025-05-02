import streamlit as st
import mysql.connector
import pandas as pd

# Streamlit page setup
st.set_page_config(layout="wide")
st.title("NASA Asteroid Data Analysis")

# Sidebar to show full data tables
st.sidebar.header("View Full Tables")
if st.sidebar.checkbox("Show Asteroids Table"):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Mama@4924",
        database="astroid_data"
    )
    df_asteroids = pd.read_sql("SELECT * FROM asteroids", conn)
    st.sidebar.write(df_asteroids)
    conn.close()

if st.sidebar.checkbox("Show Close Approach Table"):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Mama@4924",
        database="astroid_data"
    )
    df_approach = pd.read_sql("SELECT * FROM close_approach", conn)
    st.sidebar.write(df_approach)
    conn.close()

# Dropdown menu
selected_option = st.selectbox("Select any analysis", [
    "Count how many times each asteroid has approached Earth",
    "Average velocity of each asteroid over multiple approaches",
    "List top 10 fastest asteroids",
    "Find potentially hazardous asteroids that have approached Earth more than 3 times",
    "Find the month with the most asteroid approaches",
    "Get the asteroid with the fastest ever approach speed",
    "Sort asteroids by maximum estimated diameter (descending)",
    "Asteroids whose closest approach is getting nearer over time(Hint: Use ORDER BY close_approach_date and look at miss_distance)",
    "Display the name of each asteroid along with the date and miss distance of its closest approach to Earth.",
    "List names of asteroids that approached Earth with velocity > 50,000 km/h",
    "Count how many approaches happened per month",
    "Find asteroid with the highest brightness (lowest magnitude value)",
    "Get number of hazardous vs non-hazardous asteroids",
    "Find asteroids that passed closer than the Moon (lesser than 1 LD), along with their close approach date and distance.",
    "Find asteroids that came within 0.05 AU(astronomical distance)"
])


if st.button("Run Analysis"):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Mama@4924",
        database="astroid_data"
    )
    cursor = conn.cursor()

    if selected_option == "Count how many times each asteroid has approached Earth":
        query = """
            SELECT neo_reference_id, COUNT(*) AS approach_count
            FROM close_approach
            GROUP BY neo_reference_id
            ORDER BY approach_count DESC;
        """
        columns = ["Asteroid ID", "Approach Count"]

    elif selected_option == "Average velocity of each asteroid over multiple approaches":
        query = """
            SELECT neo_reference_id, AVG(relative_velocity_kmph) AS average_velocity
            FROM close_approach
            GROUP BY neo_reference_id
            ORDER BY average_velocity DESC;
        """
        columns = ["Asteroid ID", "Average Velocity (km/h)"]

    elif selected_option == "List top 10 fastest asteroids":
        query = """
            SELECT neo_reference_id, relative_velocity_kmph
            FROM close_approach
            ORDER BY relative_velocity_kmph DESC
            LIMIT 10;
        """
        columns = ["Asteroid ID", "Velocity (km/h)"]

    elif selected_option == "Find potentially hazardous asteroids that have approached Earth more than 3 times":
        query = """
            SELECT a.neo_reference_id, a.name, COUNT(c.neo_reference_id) AS approach_count
            FROM asteroids a
            JOIN close_approach c ON a.neo_reference_id = c.neo_reference_id
            WHERE a.is_potentially_hazardous_asteroid = 1
            GROUP BY a.neo_reference_id, a.name
            HAVING approach_count > 3
            ORDER BY approach_count DESC;
        """
        columns = ["Asteroid ID", "Name", "Approach Count"]

    elif selected_option == "Find the month with the most asteroid approaches":
        query = """
            SELECT MONTH(close_approach_date) AS month, COUNT(*) AS approach_count
            FROM close_approach
            GROUP BY month
            ORDER BY approach_count DESC;
        """
        columns = ["Month", "Approach Count"]

    elif selected_option == "Get the asteroid with the fastest ever approach speed":
        query = """
            SELECT neo_reference_id, relative_velocity_kmph
            FROM close_approach
            ORDER BY relative_velocity_kmph DESC
            LIMIT 1;
        """
        columns = ["Asteroid ID", "Max Velocity (km/h)"]

    elif selected_option == "Sort asteroids by maximum estimated diameter (descending)":
        query = """
            SELECT neo_reference_id, name, estimated_diameter_max_km
            FROM asteroids
            ORDER BY estimated_diameter_max_km DESC;
        """
        columns = ["Asteroid ID", "Name", "Max Diameter (km)"]

    elif selected_option == "Asteroids whose closest approach is getting nearer over time(Hint: Use ORDER BY close_approach_date and look at miss_distance)":
        query = """
            SELECT neo_reference_id, close_approach_date, miss_distance_km
            FROM close_approach
            ORDER BY neo_reference_id, close_approach_date ASC;
        """
        columns = ["Asteroid ID", "Date", "Miss Distance (km)"]

    elif selected_option == "Display the name of each asteroid along with the date and miss distance of its closest approach to Earth.":
        query = """
            SELECT a.name, c.close_approach_date, c.miss_distance_km
            FROM asteroids a
            JOIN close_approach c ON a.neo_reference_id = c.neo_reference_id
            ORDER BY c.miss_distance_km ASC
            LIMIT 1;
        """
        columns = ["Name", "Date", "Miss Distance (km)"]

    elif selected_option == "List names of asteroids that approached Earth with velocity > 50,000 km/h":
        query = """
            SELECT DISTINCT a.name, c.relative_velocity_kmph
            FROM asteroids a
            JOIN close_approach c ON a.neo_reference_id = c.neo_reference_id
            WHERE c.relative_velocity_kmph > 50000
            ORDER BY c.relative_velocity_kmph DESC;
        """
        columns = ["Name", "Velocity (km/h)"]

    elif selected_option == "Count how many approaches happened per month":
        query = """
            SELECT MONTH(close_approach_date) AS month, COUNT(*) AS total_approaches
            FROM close_approach
            GROUP BY month
            ORDER BY total_approaches DESC;
        """
        columns = ["Month", "Total Approaches"]

    elif selected_option == "Find asteroid with the highest brightness (lowest magnitude value)":
        query = """
            SELECT name, absolute_magnitude_h
            FROM asteroids
            ORDER BY absolute_magnitude_h ASC
            LIMIT 1;
        """
        columns = ["Name", "Brightness (Mag)"]

    elif selected_option == "Get number of hazardous vs non-hazardous asteroids":
        query = """
            SELECT is_potentially_hazardous_asteroid, COUNT(*) AS count
            FROM asteroids
            GROUP BY is_potentially_hazardous_asteroid;
        """
        columns = ["Hazardous (1=True, 0=False)", "Count"]

    elif selected_option == "Find asteroids that passed closer than the Moon (lesser than 1 LD), along with their close approach date and distance.":
        query = """
            SELECT neo_reference_id, close_approach_date, miss_distance_lunar
            FROM close_approach
            WHERE miss_distance_lunar < 1;
        """
        columns = ["Asteroid ID", "Date", "Miss Distance (Lunar)"]

    elif selected_option == "Find asteroids that came within 0.05 AU(astronomical distance)":
        query = """
            SELECT neo_reference_id, close_approach_date, astronomical
            FROM close_approach
            WHERE astronomical < 0.05;
        """
        columns = ["Asteroid ID", "Date", "Distance (AU)"]

    cursor.execute(query)
    results = cursor.fetchall()
    df = pd.DataFrame(results, columns=columns)
    st.dataframe(df, use_container_width=True)

    cursor.close()
    conn.close()


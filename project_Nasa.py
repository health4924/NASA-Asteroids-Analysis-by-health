
import streamlit as st
import pandas as pd
import mysql.connector
from datetime import date


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Mama@4924",  
        database="astroid_data"
    )


st.set_page_config(page_title="NASA Asteroid Tracker", layout="wide")
st.title("NASA Asteroid Tracker")


st.header("Filter Criteria")

col1, col2 = st.columns(2)

with col1:
    mag_range = st.slider("Magnitude Range", 10.0, 35.0, (13.8, 32.61))
    min_dia_range = st.slider("Min Estimated Diameter (km)", 0.0, 5.0, (0.0, 4.62))
    max_dia_range = st.slider("Max Estimated Diameter (km)", 0.0, 12.0, (0.0, 10.33))

with col2:
    velocity_range = st.slider("Relative Velocity (kmph)", 1000.0, 180000.0, (1418.21, 173071.83))
    au_range = st.slider("Astronomical Unit", 0.0, 0.5, (0.0, 0.5))
    hazard_only = st.selectbox("Only Show Potentially Hazardous", [0, 1], index=0)

start_date = st.date_input("Start Date", date(2024, 1, 1))
end_date = st.date_input("End Date", date(2025, 4, 13))


if st.button("Apply Filters"):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                a.id AS asteroid_id,
                a.name,
                a.absolute_magnitude_h,
                a.estimated_diameter_min_km,
                a.estimated_diameter_max_km,
                a.is_potentially_hazardous_asteroid,
                c.close_approach_date,
                c.relative_velocity_kmph,
                c.astronomical
            FROM asteroids a
            JOIN close_approach c ON a.id = c.neo_reference_id
            WHERE a.absolute_magnitude_h BETWEEN %s AND %s
              AND a.estimated_diameter_min_km BETWEEN %s AND %s
              AND a.estimated_diameter_max_km BETWEEN %s AND %s
              AND c.relative_velocity_kmph BETWEEN %s AND %s
              AND c.astronomical BETWEEN %s AND %s
              AND c.close_approach_date BETWEEN %s AND %s
              AND a.is_potentially_hazardous_asteroid >= %s
        """

        params = (
            mag_range[0], mag_range[1],
            min_dia_range[0], min_dia_range[1],
            max_dia_range[0], max_dia_range[1],
            velocity_range[0], velocity_range[1],
            au_range[0], au_range[1],
            start_date, end_date,
            hazard_only
        )

        cursor.execute(query, params)
        results = cursor.fetchall()
        df = pd.DataFrame(results)

        st.subheader("Filtered Asteroids")
        if df.empty:
            st.warning("No results found for the selected filters.")
        else:
            st.dataframe(df)

    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()


st.header("Run Predefined Analysis")

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
    try:
        conn = get_connection()
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
                SELECT a.id AS asteroid_id, a.name, COUNT(c.neo_reference_id) AS approach_count
                FROM asteroids a
                JOIN close_approach c ON a.id = c.neo_reference_id
                WHERE a.is_potentially_hazardous_asteroid = 1
                GROUP BY a.id, a.name
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
                SELECT id, name, estimated_diameter_max_km
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
                JOIN close_approach c ON a.id = c.neo_reference_id
                ORDER BY c.miss_distance_km ASC
                LIMIT 1;
            """
            columns = ["Name", "Date", "Miss Distance (km)"]

        elif selected_option == "List names of asteroids that approached Earth with velocity > 50,000 km/h":
            query = """
                SELECT DISTINCT a.name, c.relative_velocity_kmph
                FROM asteroids a
                JOIN close_approach c ON a.id = c.neo_reference_id
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

    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

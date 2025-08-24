# --------------------------------------------------------------------------
# RWAP Project: Asset Valuation and Analysis Dashboard
# --------------------------------------------------------------------------

# Step 1: Import necessary libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# Step 2: Set up the page configuration for a wide layout
st.set_page_config(layout="wide")

# Step 3: Define a function to load the data with error handling
# This makes the app more robust.
@st.cache_data
def load_data(filepath):
    """
    Loads the cleaned asset valuation data from a CSV file.
    Uses caching to improve performance by loading data only once.
    """
    try:
        data = pd.read_csv(filepath)
        return data
    except FileNotFoundError:
        st.error(f"Error: The file '{filepath}' was not found. Please make sure it's in the same directory as app.py.")
        return None

# Step 4: Load the dataset
df = load_data("cleaned_asset_valuation.csv")

# Only proceed if the data was loaded successfully
if df is not None:
    # Step 5: Create the main title for the dashboard
    st.title("🏛️ Real Property Asset Analysis Dashboard")
    st.markdown("An interactive dashboard for analyzing the value and distribution of real property assets.")

    # --- Section 1: Key Performance Indicators (KPIs) ---
    st.header("📈 Portfolio Overview")

    # Calculate the KPIs
    total_assets = len(df)
    total_value = df['Estimated Asset Value (USD)'].sum()
    # Count assets where 'Missing Valuation' is False
    assets_with_valuation = df['Missing Valuation'].value_counts().get(False, 0)

    # Use columns to display KPIs side-by-side
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Assets", f"{total_assets:,}")
    col2.metric("Total Estimated Value", f"${total_value/1e12:.2f} Trillion")
    col3.metric("Assets with Valuation", f"{assets_with_valuation:,}")

    st.markdown("---") # Visual separator

    # --- Section 2: Geospatial Analysis ---
    st.header("🗺️ Geospatial Distribution of Assets")

    # Prepare data for the map (remove assets with no location or value)
    df_map = df.dropna(subset=['Latitude', 'Longitude', 'Estimated Asset Value (USD)'])

    # Create a Folium map centered on the USA
    m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)

    # Add circle markers for each asset
    for idx, row in df_map.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=5,
            popup=f"<b>{row['Real Property Asset Name']}</b><br>Value: ${row['Estimated Asset Value (USD)']:,.0f}",
            tooltip=row['Real Property Asset Name'],
            color='#007bff', # A nice blue color
            fill=True,
            fill_color='#007bff'
        ).add_to(m)

    # Display the map in the Streamlit app
    st_folium(m, width=725, height=500, returned_objects=[])

    # --- Section 3: Value Analysis by State ---
    st.header("📊 Value Analysis by State")

    # Group data by state and sum the values
    value_by_state = df.groupby('State')['Estimated Asset Value (USD)'].sum().sort_values(ascending=False).reset_index()

    # Create an interactive bar chart with Plotly
    fig = px.bar(
        value_by_state.head(10),
        x='State',
        y='Estimated Asset Value (USD)',
        title='Top 10 States by Total Asset Value',
        labels={'State': 'State', 'Estimated Asset Value (USD)': 'Total Estimated Value (USD)'},
        color='State' # Add color to make it more visually appealing
    )
    # Display the Plotly chart
    st.plotly_chart(fig, use_container_width=True)


    # --- Section 4: Raw Data Exploration ---
    st.header("📋 Explore the Data")
    if st.checkbox("Show Raw Data Table"):
        st.dataframe(df)
""""
Name: Lena Phung
CS230: Section 2
Data: Skyscrapers (from Kaggle)
URL: Not Uploaded.

Description:

This program is a data analysis tool that visualizes information about skyscrapers, allowing users to filter by City and number of top skyscrapers to put on the Charts.
It generates bar charts, pie charts, and a map, displaying key statistics like the tallest skyscraper, average height, and Material  distribution.
The program also provides a pivot table for average height by state.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_folium import folium_static
import folium

# [DA1] Clean the data
# [PY3] Error checking with try/except
def clean_data(df):
    try:
        df = df.dropna(subset=['location.latitude', 'location.longitude', 'statistics.height'])
        df['statistics.height_meters'] = df['statistics.height']  # Ensure height is in meters
        return df
    except KeyError as e:
        st.error(f"KeyError: {e}. Please check the dataset structure.")
        return pd.DataFrame()

# [PY2] Function returning multiple values
# [DA2] Sort data in descending order
# [DA3] Find Top largest values of a column
def calculate_top_skyscrapers(df, top_n=10):
    top_df = df.nlargest(top_n, 'statistics.height')
    avg_height = df['statistics.height'].mean()
    return top_df, avg_height

# [PY5] Dictionary example
skyscraper_stats = {
    "total": lambda df: df.shape[0],
    "tallest": lambda df: df.loc[df['statistics.height'].idxmax()]['name'],
    "shortest": lambda df: df.loc[df['statistics.height'].idxmin()]['name']
}

# [DA7] Add/drop/select/create new/group columns
def enhance_data(df):
    df['height_category'] = df['statistics.height'].apply(lambda x: 'Tall' if x > 300 else 'Short')
    df['height_in_feet'] = df['statistics.height'] * 3.28084  # Convert meters to feet
    return df

# [PY3] Error checking with try/except
# Load and clean data
file_path = 'skyscrapers.csv'  # Replace with actual file path
try:
    data = pd.read_csv(file_path)
    data = clean_data(data)
    data = enhance_data(data)
except FileNotFoundError:
    st.error("File not found. Please upload the correct file.")
    data = pd.DataFrame()

# [ST4] Streamlit Sidebar & [ST2] Streamlit Slider
st.set_page_config(page_title="Skyscraper Visualizations", layout="wide")
st.title("Skyscraper Data Insights")

# Sidebar for filtering
# [ST1] Streamlit Textbox
# [ST3] Streamlit Multi-Select
top_n = st.sidebar.slider("Select number of top skyscrapers", min_value=5, max_value=50, value=10)
city_options = ["ALL"] + list(data['location.city'].unique())
selected_city = st.sidebar.multiselect("Filter by city", options=city_options, default="ALL")

# [DA4, DA5] Filter data
if "ALL" in selected_city:
    filtered_data = data
else:
    filtered_data = data[data['location.city'].isin(selected_city)]

# [PY3] Error checking with try/except
# [DA3] Find Top largest values of a column
try:
    top_skyscrapers, avg_height = calculate_top_skyscrapers(filtered_data, top_n)
    st.write(f"The average height of skyscrapers is {avg_height:.2f} meters.")
except Exception as e:
    st.error(f"An error occurred: {e}")

# [VIZ1] Bar chart of top skyscrapers See Section 1 of my Accompanying document to see how I used AI.
fig = px.bar(
    top_skyscrapers,
    x='name',
    y='statistics.height',
    color='location.city',
    labels={'statistics.height': 'Height (meters)', 'name': 'Skyscraper Name'},
    title="Top Skyscrapers by Height",
)
fig.update_layout(xaxis_tickangle=45)
st.plotly_chart(fig)

# [VIZ2] Pie chart of material distribution view Section 2 of my Accompanying document to see how I used AI.
material_counts = data['material'].value_counts()
pie_fig = px.pie(
    names=material_counts.index,
    values=material_counts.values,
    title="Distribution of Materials in Skyscrapers",
)
st.plotly_chart(pie_fig)

# [MAP] Map of skyscraper locations
map_center = [data['location.latitude'].mean(), data['location.longitude'].mean()]
skyscraper_map = folium.Map(location=map_center, zoom_start=5)
for _, row in filtered_data.iterrows():
    folium.Marker(
        location=[row['location.latitude'], row['location.longitude']],
        popup=f"{row['name']} ({row['statistics.height']} meters)",
    ).add_to(skyscraper_map)
folium_static(skyscraper_map)

# [VIZ3] Line chart of skyscraper height trends over time
if 'status.completed.year' in data.columns:
    trend_data = data.groupby('status.completed.year')['statistics.height'].mean().reset_index()
    # [DA6] Analyze data with pivot tables
    line_fig = px.line(
        trend_data,
        x='status.completed.year',
        y='statistics.height',
        title="Average Skyscraper Height by Completion Year",
        labels={'status.completed.year': 'Year', 'statistics.height': 'Average Height (meters)'}
    )
    st.plotly_chart(line_fig)

# [DA8] Iterate through rows of a DataFrame with iterrows()
st.write("Tall Skyscrapers:")
tall_skyscrapers = []
for _, row in data.iterrows():
    if row['height_category'] == 'Tall':
        tall_skyscrapers.append(f"{row['name']} - {row['statistics.height']} meters")
st.write(tall_skyscrapers)

# [PY5] Dictionary with dynamic access
# Summary statistics
st.sidebar.header("Summary Report")
filtered_stats = {
    "total": lambda df: df.shape[0],
    "tallest": lambda df: df.loc[df['statistics.height'].idxmax()]['name'] if not df.empty else "N/A",
    "shortest": lambda df: df.loc[df['statistics.height'].idxmin()]['name'] if not df.empty else "N/A"
}
for key, func in filtered_stats.items():
    try:
        st.sidebar.write(f"{key.capitalize()}: {func(filtered_data)}")
    except Exception as e:
        st.sidebar.write(f"{key.capitalize()}: Error ({e})")

# [PY1] Function with a default parameter
def display_statistics(df, metric='statistics.height'):
    """Displays statistics for a given metric."""
    return df[metric].describe()

# [PY4] List comprehension
height_descriptions = [
    f"{row['name']} ({row['statistics.height']} meters)"
    for _, row in top_skyscrapers.iterrows()
]
st.write("Skyscraper Height Statistics:")
st.write(display_statistics(data))
st.write("Top Skyscraper Descriptions:")
st.write(height_descriptions)

# [DA9] Add a new column or perform calculations on DataFrame columns
st.write("Enhanced Data with Height Category and Height in Feet:")
st.write(data[['name', 'statistics.height', 'height_category', 'height_in_feet']])

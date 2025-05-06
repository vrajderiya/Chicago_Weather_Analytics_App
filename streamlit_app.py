# streamlit_app.py
import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from windrose import WindroseAxes
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Chicago Weather Dashboard", layout="wide")
st.title("\U0001F327️ Chicago Weather Dashboard")
st.markdown("Hourly forecast data fetched from [Open-Meteo API](https://open-meteo.com/)")

@st.cache_data
def load_data():
    url = "https://api.open-meteo.com/v1/forecast?latitude=41.88&longitude=-87.63&hourly=temperature_2m,relative_humidity_2m,precipitation,cloudcover,windspeed_10m,winddirection_10m&timezone=auto"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data['hourly'])
    df['time'] = pd.to_datetime(df['time'], errors='coerce')
    for col in ['temperature_2m', 'relative_humidity_2m', 'precipitation', 'cloudcover', 'windspeed_10m', 'winddirection_10m']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['date_only'] = df['time'].dt.date
    return df

df = load_data()

# Buttons at the top
col1, col2 = st.columns([1, 1])
refresh_data = col1.button("🔄 Refresh Weather Data")
refresh_plots = col2.button("🔃 Refresh Plots")

if refresh_data:
    st.cache_data.clear()
    st.success("✅ Weather data refreshed from API!")

if refresh_plots:
    st.toast("🔁 Visualizations reloaded")

# Always (re)load data
df = load_data()

# Plot 1
variable_labels = {
    'temperature_2m': 'Temperature (°C)',
    'relative_humidity_2m': 'Humidity (%)',
    'precipitation': 'Precipitation (mm)',
    'cloudcover': 'Cloud Cover (%)'
}

selected_variable = st.selectbox("Select Variable", options=list(variable_labels.keys()), format_func=lambda x: variable_labels[x])

fig = px.line(
    df,
    x='time',
    y=selected_variable,
    title=f"{variable_labels[selected_variable]} Over Time",
    labels={'time': 'Time', selected_variable: variable_labels[selected_variable]},
    template='plotly_white'
)

fig.update_layout(
    xaxis=dict(
        tickformat='%b %d\n%H:%M',  # e.g., "May 06\n12:00"
        tickangle=0,                # Makes ticks easier to read
        dtick=43200000              # 12 hours in milliseconds
    )
)


st.plotly_chart(fig, use_container_width=True)

#writeup
st.write("""
This interactive line chart displays weather trends in Chicago over time. Users can dynamically switch between variables—Temperature, Humidity, Precipitation, and Cloud Cover—using the dropdown menu. The x-axis represents time, while the y-axis shows the corresponding value of the selected variable.

This tool allows for quick comparison of different weather factors and can help identify short-term trends and patterns in local atmospheric conditions.

Note: If the precipitation value is 0, it basically says chaces of rain are very low.""")

# Plot 2
import plotly.graph_objects as go

if not df.empty:
    st.subheader("\U0001F321️ 3D Scatterplot: Temperature, Precipitation, and Windspeed")

    fig3d = go.Figure(data=[go.Scatter3d(
        x=df['temperature_2m'],
        y=df['precipitation'],
        z=df['windspeed_10m'],
        mode='markers',
        marker=dict(
            size=5,
            color=df['temperature_2m'],      # Color by temperature
            colorscale='thermal',
            opacity=0.8,
            colorbar=dict(title='Temp (°C)'),
            line=dict(width=0.5, color='black')
        ),
        hovertemplate=
            'Temp: %{x}°C<br>' +
            'Precip: %{y} mm<br>' +
            'Wind: %{z} km/h'
    )])

    fig3d.update_layout(
        scene=dict(
            xaxis_title='Temperature (°C)',
            yaxis=dict(
            title='Precipitation (mm)',
            range=[0, 1]  # Set precipitation range
        ),
            zaxis_title='Windspeed (km/h)'
        ),
        margin=dict(l=0, r=0, b=0, t=40),
        height=600
    )

    st.plotly_chart(fig3d, use_container_width=True)

#writeup
st.markdown('<p style="font-size:22px; font-weight:bold;">3D Visualization of Forecasted Temperature, Precipitation, and Windspeed in Chicago</p>', unsafe_allow_html=True)

st.write("""3D Visualization of Forecasted Temperature, Precipitation, and Windspeed in Chicago

The 3D scatterplot above offers a multidimensional representation of forecasted hourly weather data for Chicago, bringing together three key atmospheric variables: temperature (°C), precipitation (mm), and windspeed (km/h). Each data point in the plot corresponds to an individual hour within the forecast period.

The X-axis indicates the air temperature measured in degrees Celsius. This variable is also used to color-code the data points, with a gradient transitioning from cool blues (lower temperatures) to warm reds (higher temperatures). The Y-axis represents the precipitation values in millimeters. This axis helps track moisture levels and potential rainfall accumulation. The Z-axis captures the windspeed in kilometers per hour, a vital component of local weather that can influence conditions like wind chill or the spread of precipitation. A color bar on the right reinforces the temperature scale applied to each point, enhancing visual readability and temperature-based clustering. The plot will let users observe whether higher temperatures are associated with calmer or stronger winds, or identify clusters of data where precipitation levels peak.""")

# Plot 3
st.subheader("\U0001F4CA Temperature Summary by Day")

grouped = df.groupby('date_only')['temperature_2m'].agg(['min', 'mean', 'max']).reset_index()

if not grouped.empty:
    date_options = grouped['date_only'].astype(str).tolist()
    selected_date_str = st.selectbox("Select Date:", options=date_options)
    selected_date = pd.to_datetime(selected_date_str).date()
    day_data = grouped[grouped['date_only'] == selected_date].iloc[0]


    fig_bar = go.Figure(
        data=[
            go.Bar(
                x=['Min', 'Mean', 'Max'],
                y=day_data[['min', 'mean', 'max']].values,
                marker_color='#76b5c5'
            )
        ]
    )
    fig_bar.update_layout(
        title=f"Temperature Summary for {selected_date}",
        yaxis_title="Temperature (°C)"
    )
    
    fig_bar.update_yaxes(range=[0, 30])
    
    st.plotly_chart(fig_bar)

#writeup
st.write("""This interactive bar chart presents a temperature summary for a selected day based on hourly weather forecast data. It displays three key metrics for that day:

Minimum temperature Average (mean) temperature Maximum temperature All values are shown in degrees Celsius (°C), providing a concise yet informative snapshot of how temperatures fluctuate throughout the day.

The user can adjust the day using the slider above the chart. As the slider value changes, the chart dynamically updates to reflect the corresponding temperature statistics for the newly selected day. This allows for quick comparisons across different dates and helps identify patterns such as warming or cooling trends over the forecast period.

This visualization is particularly useful for identifying temperature ranges and daily variability, making it ideal for planning activities or analyzing weather patterns in a user-friendly format.""")

# Plot 4

def plot_wind_boxplot(df):
    df['date_only'] = pd.to_datetime(df['time']).dt.date
    df['date_str'] = df['date_only'].astype(str)  # Needed for coloring

    fig = px.box(
        df,
        x='date_str',
        y='windspeed_10m',
        color='date_str',  # Different color for each box
        title='Daily Wind Speed Distribution in Chicago (km/h)',
        labels={'date_str': 'Date', 'windspeed_10m': 'Wind Speed (km/h)'},
    )

    fig.update_layout(
        showlegend=False,
        xaxis_tickangle=-45,
        margin=dict(l=40, r=20, t=60, b=60),
        height=500,
        template='plotly_white'
    )
    fig.update_traces(marker=dict(line=dict(width=1, color='black')))
    st.plotly_chart(fig, use_container_width=True)

df = load_data()  

if not df.empty:
    plot_wind_boxplot(df)


#writeup
st.markdown('<p style="font-size:22px; font-weight:bold;">Daily Wind Speed Distribution in Chicago (km/h)</p>', unsafe_allow_html=True)

st.write("""This box plot represents the forecasted distribution of hourly wind speeds in Chicago over a one-week period. Each box corresponds to a specific date and summarizes the variability and range of wind speeds expected on that day.""")

st.markdown('<p style="font-size:22px; font-weight:bold;">📊 How to interpret the plot:</p>', unsafe_allow_html=True)

st.write("""Boxes (Interquartile Range - IQR): Each box captures the middle 50% of wind speed values for the day — from the 25th percentile (Q1) to the 75th percentile (Q3). This shows the core range of expected wind speeds.

Horizontal line within each box: Indicates the median wind speed, offering a measure of central tendency for that day.

Whiskers: Extend to the most extreme data points within 1.5 times the IQR from Q1 and Q3. These represent the range of typical wind speeds, excluding extreme outliers.

Individual points beyond whiskers: Plotted as outliers, these represent potential instances of unusually low or high wind speeds.

Color coding: Different colors are used to distinguish each day's distribution visually and enhance readability.""")

st.markdown('<p style="font-size:22px; font-weight:bold;">🌆 Contextual Note:</p>', unsafe_allow_html=True)

st.write("""Given that Chicago is popularly known as the “Windy City,” analyzing wind speed patterns is both relevant and practical. This type of visualization helps users anticipate variability and understand daily wind dynamics at a glance — crucial for sectors like aviation, infrastructure, logistics, and public planning.

The plot provides a compact summary of variability across multiple days, making it ideal for comparing trends, assessing forecast consistency, and communicating expectations effectively.""")
#######################################################################

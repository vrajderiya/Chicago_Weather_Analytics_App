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

# Dropdown to select variable
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

st.plotly_chart(fig, use_container_width=True)

# 3D Scatter Plot
if not df.empty:
    st.subheader("\U0001F321️ 3D Scatterplot: Temperature, Precipitation, and Windspeed")
    fig3d = plt.figure(figsize=(8, 4))
    ax = fig3d.add_subplot(111, projection='3d')
    scatter = ax.scatter(df['temperature_2m'], df['precipitation'], df['windspeed_10m'],
                         c=df['temperature_2m'], cmap='coolwarm', s=20, alpha=0.7, edgecolors='black')
    ax.set_xlabel('Temperature (°C)')
    ax.set_ylabel('Precipitation')
    ax.set_zlabel('Windspeed (km/h)')
    plt.colorbar(scatter, ax=ax, label='Temperature (°C)')
    st.pyplot(fig3d)

# Daily Summary
st.subheader("\U0001F4CA Temperature Summary by Day")
grouped = df.groupby('date_only')['temperature_2m'].agg(['min', 'mean', 'max']).reset_index()

if not grouped.empty:
    day_index = st.slider("Select Day Index:", min_value=0, max_value=len(grouped) - 1, step=1)
    selected_date = grouped.iloc[day_index]['date_only']
    day_data = grouped.iloc[day_index]

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
    st.plotly_chart(fig_bar)

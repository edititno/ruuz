# Ruuz Analytics Dashboard v1.0
# Visual dashboard for Ruuz weather and context data

import streamlit as st
import pandas as pd
import sqlite3
import os

# Page setup
st.set_page_config(page_title='Ruuz Analytics', layout='wide')
st.title('Ruuz Analytics Dashboard')
st.markdown('Real-time context data from the Ruuz Commerce Engine')
st.markdown('---')

# Load data
DB_FILE = 'ruuz.db'
CSV_FILE = 'ruuz_data.csv'

if not os.path.exists(DB_FILE):
    st.error('Database not found. Run ruuz_db.py first.')
    st.stop()

conn = sqlite3.connect(DB_FILE)
df = pd.read_sql('SELECT * FROM weather_logs', conn)
conn.close()

# Top stats row
st.markdown('### Overview')
col1, col2, col3, col4 = st.columns(4)
col1.metric('Total Records', len(df))
col2.metric('Cities Tracked', df['city'].nunique())
col3.metric('Sunny Moods', len(df[df['mood'] == 'sunny']))
col4.metric('Rainy Moods', len(df[df['mood'] == 'rainy']))

st.markdown('---')

# Two charts side by side
left_col, right_col = st.columns(2)

# Chart 1: Mood count by city
with left_col:
    st.markdown('### Mood Distribution by City')
    mood_by_city = df.groupby(['city', 'mood']).size().reset_index(name='count')
    mood_pivot = mood_by_city.pivot(index='city', columns='mood', values='count').fillna(0)
    st.bar_chart(mood_pivot)

# Chart 2: Average temperature by city
with right_col:
    st.markdown('### Average Temperature by City')
    avg_temp = df.groupby('city')['temp'].mean().sort_values(ascending=False)
    st.bar_chart(avg_temp)

st.markdown('---')

# Two more charts
left_col2, right_col2 = st.columns(2)

# Chart 3: Humidity by mood
with left_col2:
    st.markdown('### Average Humidity by Mood')
    humidity_by_mood = df.groupby('mood')['humidity'].mean()
    st.bar_chart(humidity_by_mood)

# Chart 4: Wind speed by city
with right_col2:
    st.markdown('### Average Wind Speed by City')
    wind_by_city = df.groupby('city')['wind_speed'].mean().sort_values(ascending=False)
    st.bar_chart(wind_by_city)

st.markdown('---')

# Filter section
st.markdown('### Explore the Data')
selected_mood = st.selectbox('Filter by mood:', ['All', 'sunny', 'rainy'])

if selected_mood == 'All':
    filtered_df = df
else:
    filtered_df = df[df['mood'] == selected_mood]

st.dataframe(filtered_df[['timestamp', 'city', 'weather', 'temp', 'feels_like', 'humidity', 'wind_speed', 'time_of_day', 'mood']], use_container_width=True)

st.markdown('---')
st.markdown(f'*Dashboard generated from {len(df)} records across {df["city"].nunique()} cities*')

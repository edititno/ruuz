# Ruuz Analytics Dashboard v2.0
# Visual dashboard with weather, UV, and air quality data

import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title='Ruuz Analytics', layout='wide')
st.title('Ruuz Analytics Dashboard')
st.markdown('Real-time context data from the Ruuz Commerce Engine')
st.markdown('---')

DB_FILE = 'ruuz.db'

if not os.path.exists(DB_FILE):
    st.error('Database not found. Run ruuz_db.py first.')
    st.stop()

conn = sqlite3.connect(DB_FILE)
df = pd.read_sql('SELECT * FROM weather_logs', conn)
conn.close()

# Top stats
st.markdown('### Overview')
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric('Total Records', len(df))
col2.metric('Cities', df['city'].nunique())
col3.metric('Sunny Moods', len(df[df['mood'] == 'sunny']))
col4.metric('Rainy Moods', len(df[df['mood'] == 'rainy']))
col5.metric('UV Alerts', len(df[df['uv_alert'] == 'high']))
col6.metric('Air Alerts', len(df[df['air_alert'] == 'poor']))

st.markdown('---')

# Row 1: Mood and Temperature
left, right = st.columns(2)

with left:
    st.markdown('### Mood Distribution by City')
    mood_by_city = df.groupby(['city', 'mood']).size().reset_index(name='count')
    mood_pivot = mood_by_city.pivot(index='city', columns='mood', values='count').fillna(0)
    st.bar_chart(mood_pivot)

with right:
    st.markdown('### Average Temperature by City')
    avg_temp = df.groupby('city')['temp'].mean().sort_values(ascending=False)
    st.bar_chart(avg_temp)

st.markdown('---')

# Row 2: UV and Air Quality
left2, right2 = st.columns(2)

with left2:
    st.markdown('### Average UV Index by City')
    avg_uv = df.groupby('city')['uv_index'].mean().sort_values(ascending=False)
    st.bar_chart(avg_uv)

with right2:
    st.markdown('### Air Quality Distribution')
    air_dist = df['air_quality_label'].value_counts()
    st.bar_chart(air_dist)

st.markdown('---')

# Row 3: Humidity and Wind
left3, right3 = st.columns(2)

with left3:
    st.markdown('### Average Humidity by Mood')
    humidity_by_mood = df.groupby('mood')['humidity'].mean()
    st.bar_chart(humidity_by_mood)

with right3:
    st.markdown('### Average Wind Speed by City')
    wind_by_city = df.groupby('city')['wind_speed'].mean().sort_values(ascending=False)
    st.bar_chart(wind_by_city)

st.markdown('---')

# Alert table
st.markdown('### Alert Records')
alerts = df[(df['uv_alert'] == 'high') | (df['air_alert'] == 'poor')]
if len(alerts) > 0:
    st.dataframe(alerts[['timestamp', 'city', 'temp', 'uv_index', 'uv_alert', 'air_quality_label', 'air_alert', 'mood']], use_container_width=True)
else:
    st.info('No UV or air quality alerts recorded yet.')

st.markdown('---')

# Full data explorer
st.markdown('### Explore the Data')
selected_mood = st.selectbox('Filter by mood:', ['All', 'sunny', 'rainy'])

if selected_mood == 'All':
    filtered_df = df
else:
    filtered_df = df[df['mood'] == selected_mood]

st.dataframe(filtered_df[['timestamp', 'city', 'weather', 'temp', 'feels_like', 'humidity', 'wind_speed', 'uv_index', 'uv_alert', 'air_quality_label', 'air_alert', 'time_of_day', 'mood']], use_container_width=True)

st.markdown('---')
st.markdown(f'*Dashboard v2.0 — {len(df)} records across {df["city"].nunique()} cities — signals: weather, UV index, air quality*')

# Ruuz Analytics Dashboard v3.0
# Visual dashboard with weather, UV, air quality, and holiday data

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
col5.metric('UV Alerts', len(df[df['uv_alert'].isin(['high', 'very-high', 'extreme'])]))
col6.metric('Holidays', len(df[df['holiday'] != 'none']))

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
    st.markdown('### UV Alert Distribution')
    uv_dist = df['uv_alert'].value_counts()
    st.bar_chart(uv_dist)

st.markdown('---')

# Row 3: Air Quality and Wind
left3, right3 = st.columns(2)

with left3:
    st.markdown('### Air Quality Distribution')
    air_dist = df['air_quality_label'].value_counts()
    st.bar_chart(air_dist)

with right3:
    st.markdown('### Average Wind Speed by City')
    wind_by_city = df.groupby('city')['wind_speed'].mean().sort_values(ascending=False)
    st.bar_chart(wind_by_city)

st.markdown('---')

# Row 4: Humidity
st.markdown('### Average Humidity by Mood')
left4, right4 = st.columns(2)

with left4:
    humidity_by_mood = df.groupby('mood')['humidity'].mean()
    st.bar_chart(humidity_by_mood)

with right4:
    st.markdown('#### Humidity Insight')
    rainy_humidity = df[df['mood'] == 'rainy']['humidity'].mean()
    sunny_humidity = df[df['mood'] == 'sunny']['humidity'].mean()
    if len(df) > 0:
        st.write(f'Rainy mood avg humidity: {rainy_humidity:.0f}%')
        st.write(f'Sunny mood avg humidity: {sunny_humidity:.0f}%')
        st.write(f'Difference: {abs(rainy_humidity - sunny_humidity):.0f}%')

st.markdown('---')

# Alert table
st.markdown('### Alert Records (UV, Air Quality, Holidays)')
alerts = df[(df['uv_alert'].isin(['high', 'very-high', 'extreme'])) | (df['air_alert'] == 'poor') | (df['holiday'] != 'none')]
if len(alerts) > 0:
    st.dataframe(alerts[['timestamp', 'city', 'country', 'temp', 'uv_index', 'uv_alert', 'air_quality_label', 'air_alert', 'holiday', 'mood']], use_container_width=True)
else:
    st.info('No alerts recorded yet.')

st.markdown('---')

# Holiday section
st.markdown('### Holiday Records')
holidays = df[df['holiday'] != 'none']
if len(holidays) > 0:
    st.dataframe(holidays[['timestamp', 'city', 'country', 'holiday', 'weather', 'temp', 'mood']], use_container_width=True)
else:
    st.info('No holidays recorded yet. Run the logger on a public holiday to capture data.')

st.markdown('---')

# Full data explorer
st.markdown('### Explore the Data')

filter_col1, filter_col2 = st.columns(2)
with filter_col1:
    selected_mood = st.selectbox('Filter by mood:', ['All', 'sunny', 'rainy'])
with filter_col2:
    selected_city = st.selectbox('Filter by city:', ['All'] + sorted(df['city'].unique().tolist()))

filtered_df = df.copy()
if selected_mood != 'All':
    filtered_df = filtered_df[filtered_df['mood'] == selected_mood]
if selected_city != 'All':
    filtered_df = filtered_df[filtered_df['city'] == selected_city]

st.dataframe(filtered_df[['timestamp', 'city', 'country', 'weather', 'temp', 'feels_like', 'humidity', 'wind_speed', 'uv_index', 'uv_alert', 'air_quality_label', 'air_alert', 'holiday', 'time_of_day', 'mood']], use_container_width=True)

st.markdown('---')
st.markdown(f'*Dashboard v3.0 — {len(df)} records across {df["city"].nunique()} cities — signals: weather, UV index, air quality, holidays*')

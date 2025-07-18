import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import re

# --- Load and Preprocess Dataset ---
df = pd.read_csv("C:\\Users\\sayed\\OneDrive\\Desktop\\Major PRO\\naukri_data_science_jobs_india.csv")

# Rename columns to match expected names
df.rename(columns={
    'Job Title': 'Job_Role',
    'Company': 'Company',
    'Location': 'Location',
    'Job Experience': 'Job Experience',
    'Skills/Description': 'Skills/Description'
}, inplace=True)

# Extract or simulate posted date
df['Posted Date'] = pd.to_datetime(df['Job Experience'].apply(
    lambda x: datetime.now() - timedelta(days=int(re.search(r'\d+', str(x)).group())*7
    if pd.notnull(x) and re.search(r'\d+', str(x)) else 14)))

# Clean columns
df['Location'] = df['Location'].astype(str).str.split(',').str[0].str.strip()
df['Job_Role'] = df['Job_Role'].astype(str).str.strip().str.title()
df['Experience Min'] = df['Job Experience'].str.extract(r'(\d+)').astype(float)
df.dropna(subset=['Location'], inplace=True)

# --- Streamlit App Setup ---
st.set_page_config(page_title="📊 DS Job Dashboard", layout="wide", initial_sidebar_state="expanded")

# --- Custom Dark Style ---
st.markdown("""
<style>
body {
    background-color: #A0C3E0;
    color: black;
}
.sidebar .sidebar-content {
    background-color:  #e8f0f8;
}
[data-testid="stMetric"] {
    border-radius: 12px;
    padding: 20px;
    color: black;
    font-weight: bold;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
             background-color: #d6e5f5;
}
</style>
""", unsafe_allow_html=True)

st.markdown("##  Job Posting Dashboard")

# --- Sidebar Filters ---
with st.sidebar:
    st.header("🔍 Filter Jobs")

    # Define top 20 roles based on frequency
    top_20_roles = [
        "Data Engineer", "Data Scientist", "Data Analyst",
        "Senior Technical Lead (Data Engineer)", "Senior Data Engineer",
        "Business Analyst", "Senior Data Scientist", "Azure Data Engineer",
        "Data Engineer: Data Integration", "Big Data Engineer", "Senior Data Analyst",
        "Big Data Developer", "Data Engineer: Big Data", "Lead Data Engineer",
        "Senior Software Engineer", "Senior Business Analyst", "Product Analyst",
        "Python Developer", "Data Engineering Application Developer", "Software Engineer"
    ]

    role_filter = st.selectbox("Select Job Role", options=["All"] + top_20_roles)

    location_filter = st.multiselect("Select Job Locations", options=sorted(df['Location'].dropna().unique()))

    time_filter = st.selectbox("Job Posted", options=["All Time", "1 week ago", "2 weeks ago", "1 month ago"])

# --- Apply Filters ---
filtered_df = df.copy()

if role_filter != "All":
    filtered_df = filtered_df[filtered_df['Job_Role'] == role_filter]

if location_filter:
    filtered_df = filtered_df[filtered_df['Location'].isin(location_filter)]

if time_filter != "All Time":
    days_map = {
        "1 week ago": 7,
        "2 weeks ago": 14,
        "1 month ago": 30
    }
    cutoff = datetime.now() - timedelta(days=days_map[time_filter])
    filtered_df = filtered_df[filtered_df['Posted Date'] >= cutoff]

# --- Metrics ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📌 Total Jobs", len(filtered_df))
with col2:
    st.metric("🏙️ Locations", filtered_df['Location'].nunique())
with col3:
    st.metric("🏢 Companies", filtered_df['Company'].nunique())
with col4:
    avg_exp = filtered_df['Experience Min'].mean()
    st.metric("💼 Avg Exp (yrs)", f"{avg_exp:.1f}" if not pd.isna(avg_exp) else "N/A")

# --- Charts ---
st.markdown("### 📍 Top Locations by Job Count")
top_locations = filtered_df['Location'].value_counts().head(10).reset_index()
top_locations.columns = ['Location', 'Count']
fig1 = px.bar(top_locations, x='Location', y='Count', color='Count',
              color_continuous_scale='deep', template='plotly_dark')
st.plotly_chart(fig1, use_container_width=True)

st.markdown("### 📊 Experience Distribution")
exp_data = filtered_df.dropna(subset=['Experience Min'])
fig2 = px.histogram(exp_data, x='Experience Min', nbins=10, template='plotly_dark',
                    color_discrete_sequence=['#FFA07A'])
st.plotly_chart(fig2, use_container_width=True)

# --- Word Cloud for Skills ---
st.markdown("### ☁️ Top Skills Word Cloud")
skill_text = " ".join(filtered_df["Skills/Description"].dropna().astype(str).values).lower()
wc = WordCloud(width=1000, height=400, background_color="#0f1c2e", colormap="plasma").generate(skill_text)

fig, ax = plt.subplots(figsize=(12, 4))
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
st.pyplot(fig)

# --- Top Companies by Job Count ---
st.markdown("### 🏢 Top Hiring Companies")
top_companies = filtered_df['Company'].value_counts().head(10).reset_index()
top_companies.columns = ['Company', 'Count']
fig3 = px.bar(top_companies, x='Company', y='Count', color='Count',
              color_continuous_scale='teal', template='plotly_dark')
st.plotly_chart(fig3, use_container_width=True)

# --- Top Job Roles ---
st.markdown("### 👔 Most Common Job Roles")
top_roles = filtered_df['Job_Role'].value_counts().head(10).reset_index()
top_roles.columns = ['Job Role', 'Count']
fig4 = px.bar(top_roles, x='Job Role', y='Count', color='Count',
              color_continuous_scale='magma', template='plotly_dark')
st.plotly_chart(fig4, use_container_width=True)

# --- Experience vs Job Role (Box Plot) ---
st.markdown("### 📈 Experience Distribution by Job Role")
box_data = filtered_df[['Job_Role', 'Experience Min']].dropna()
top_5_roles = box_data['Job_Role'].value_counts().nlargest(5).index
box_data = box_data[box_data['Job_Role'].isin(top_5_roles)]
fig5 = px.box(box_data, x='Job_Role', y='Experience Min', color='Job_Role',
              template='plotly_dark', points='all')
st.plotly_chart(fig5, use_container_width=True)

import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import docx
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load NLP model
nlp = spacy.load("en_core_web_sm")

st.set_page_config(page_title=" Smart Job Recommender", layout="wide")

# Load data
@st.cache_data
def load_data():
    df1 = pd.read_csv("C:\\Users\sayed\OneDrive\Desktop\Major PRO\\merged_job_listings.csv")
    df2 = pd.read_csv("C:\\Users\sayed\OneDrive\Desktop\Major PRO\\CareerCompass_jobs_with_skills.csv")

    df1 = df1.rename(columns={
        'company': 'company_name',
        'location': 'job_location',
        'description': 'job_description',
        'link': 'apply_link',
        'skills': 'required_skills',
        'date_posted': 'job_posted_date'
    })

    df2 = df2.rename(columns={
        'job_summary': 'job_description',
        'job_location': 'job_location'
    })

    for col in set(df1.columns).union(df2.columns):
        df1[col] = df1.get(col, '')
        df2[col] = df2.get(col, '')

    df = pd.concat([df1, df2], ignore_index=True)
    for col in ['job_title', 'required_skills', 'job_description', 'job_location']:
        df[col] = df[col].fillna('').str.lower().str.strip()

    df['combined_text'] = (
        df['job_title'] + ' ' +
        df['required_skills'] + ' ' +
        df['job_description'] + ' ' +
        df['job_location']
    )
    return df

df = load_data()

@st.cache_resource
def get_vectorizer_matrix(df):
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    matrix = vectorizer.fit_transform(df['combined_text'])
    return vectorizer, matrix

vectorizer, tfidf_matrix = get_vectorizer_matrix(df)

# Custom CSS
st.markdown("""
    <style>
        .main-title {
            text-align: center;
            font-size: 32px;
            font-weight: bold;
            color: #black;
            margin-top: 10px;
        }
        .job-card {
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 10px;
            box-shadow: 0px 0px 6px #ccc;
        }
        .stTextInput > div > input {
            width: 100% !important;
        }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-title"> Resume & Preference Based Job Recommender</div>', unsafe_allow_html=True)

# Resume Parsing
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return " ".join([page.get_text() for page in doc])

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return " ".join([para.text for para in doc.paragraphs])

def extract_resume_info(text):
    doc = nlp(text)
    skills_list = [
        'python', 'java', 'c++', 'sql', 'excel', 'machine learning',
        'deep learning', 'pytorch', 'tensorflow', 'data analysis', 'cloud',
        'aws', 'azure', 'git', 'react', 'html', 'css', 'javascript'
    ]
    skills = list({token.text.lower() for token in doc if token.text.lower() in skills_list})

    education = []
    for ent in doc.ents:
        if ent.label_ == "ORG" and "university" in ent.text.lower():
            education.append(ent.text)

    return {
        "skills": ", ".join(skills),
        "education": ", ".join(education)
    }

# Form UI
with st.form("preference_form"):
    st.subheader("📝 Enter Your Preferences")

    col1, col2 = st.columns(2)
    with col1:
        job_type = st.text_input("Job Type (e.g., Data Scientist)")
        experience_level = st.selectbox("Experience Level", ["Fresher", "Experienced"])
    with col2:
        preferred_skills = st.text_input("Skills (comma-separated)")
        location = st.text_input("Preferred Location (e.g., Remote, Mumbai)")

    col3, col4 = st.columns([2, 1])
    with col3:
        career_objective = st.text_area("Career Objective (3–5 lines)", height=100)
    with col4:
        remote_only = st.checkbox("Remote Only")

    resume = st.file_uploader("📤 Upload Resume (PDF or DOCX)", type=['pdf', 'docx'])
    submit_btn = st.form_submit_button("🔎 Find Matching Jobs")

# Recommendation Logic
if submit_btn:
    if not resume:
        st.warning("⚠️ Please upload a resume.")
    else:
        with st.spinner("🔍 Analyzing your inputs..."):
            resume_text = extract_text_from_pdf(resume) if resume.name.endswith(".pdf") else extract_text_from_docx(resume)
            parsed_resume = extract_resume_info(resume_text)

            user_input_text = " ".join([
                job_type, preferred_skills, experience_level, location,
                career_objective, parsed_resume["skills"], parsed_resume["education"]
            ]).lower()

            user_vector = vectorizer.transform([user_input_text])
            similarity_scores = cosine_similarity(user_vector, tfidf_matrix).flatten()

            df['similarity_score'] = similarity_scores
            df['has_link'] = df['apply_link'].notnull() & df['apply_link'].str.startswith("http")

            top_matches = df[df['similarity_score'] > 0.2]

            if remote_only:
                top_matches = top_matches[top_matches['job_location'].str.contains("remote")]

            top_matches = top_matches.sort_values(by=['has_link', 'similarity_score'], ascending=[False, False])

            st.success(f"✅ Found {len(top_matches)} matching job(s).")

            if top_matches.empty:
                st.info("❌ No matching jobs found. Try different inputs.")
            else:
                for _, row in top_matches.iterrows():
                    with st.expander(f"🔹 {row['job_title'].title()} at {row['company_name']}"):
                        st.markdown(f"""
                            <div class="job-card">
                                <p><strong>Location:</strong> {row['job_location'].title()}</p>
                                <p><strong>Skills:</strong> {row['required_skills']}</p>
                                <p><strong>Description:</strong> {row['job_description'][:300]}...</p>
                                <p><strong>Match Score:</strong> {row['similarity_score']:.2f}</p>
                                <p><strong>Apply:</strong> <a href="{row['apply_link']}" target="_blank">{row['apply_link']}</a></p>
                                <p><strong>Posted:</strong> {row['job_posted_date']}</p>
                            </div>
                        """, unsafe_allow_html=True)

st.markdown(f"<hr><p><strong>🗂️ Total Jobs in Database:</strong> {len(df)}</p>", unsafe_allow_html=True)

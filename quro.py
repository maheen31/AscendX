import streamlit as st
import random
import os
import openai

# ----------------- CONFIG & STYLE ----------------- #
st.set_page_config(page_title="Career Compass", layout="wide")

# Custom CSS to match your image’s palette
st.markdown("""
    <style>
        body {
            background: linear-gradient(135deg, #5f2c82, #49a09d);
            color: white;
        }
        .main {
            background: rgba(0, 0, 0, 0.25);
            border-radius: 12px;
            padding: 2rem;
        }
        .stButton button {
            background-color: #1c92d2;
            color: white;
            border-radius: 8px;
        }
        .stSelectbox, .stTextInput, .stRadio {
            background-color: #ffffff10 !important;
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

# ----------------- NAVIGATION BAR ----------------- #
st.sidebar.title(" Career Toolkit")
page = st.sidebar.radio("Choose a section:", [" 5-Min Quiz", " Roadmap Generator"])

# ----------------- PAGE 1: QUIZ ----------------- #
if page == " 5-Min Quiz":
    st.title(" Job Role Knowledge Self-Check")

    question_bank = {
        "Software Developer": [
            ("What is the time complexity of binary search?", ["O(n)", "O(log n)", "O(n log n)", "O(1)"], 1),
            ("Which language is primarily used for Android development?", ["Swift", "Kotlin", "React", "C#"], 1),
            ("What does MVC stand for?", ["Model View Controller", "Manage View Control", "Main Visual Control", "Model Visual Center"], 0),
            ("What is a Git branch?", ["A copy of repository", "A pointer to commits", "A file", "A pull request"], 1),
            ("Which data structure uses FIFO order?", ["Stack", "Queue", "Linked List", "Tree"], 1),
            ("What is used to manage dependencies in Python?", ["NPM", "Composer", "pip", "Gradle"], 2),
            ("Which HTTP status code means 'Not Found'?", ["200", "301", "404", "500"], 2),
            ("What is the purpose of a constructor in OOP?", ["To destroy objects", "To create objects", "To inherit classes", "None"], 1),
            ("Which SQL command is used to remove records?", ["DELETE", "DROP", "REMOVE", "ERASE"], 0),
            ("What is a REST API?", ["A file", "A type of database", "A protocol for communication", "A compiler"], 2)
        ],
        "Data Scientist": [
            ("What is the purpose of cross-validation?", ["To split datasets", "To test accuracy", "To tune models", "All of the above"], 3),
            ("Which library is used for data manipulation in Python?", ["NumPy", "Pandas", "TensorFlow", "Matplotlib"], 1),
            ("Which metric is suitable for imbalanced classification?", ["Accuracy", "Recall", "Precision", "F1 Score"], 3),
            ("What does PCA stand for?", ["Principal Component Analysis", "Partial Correlation Analysis", "Principal Clustering Algorithm", "None"], 0),
            ("Which algorithm is used for regression?", ["Logistic", "KMeans", "Linear", "Naive Bayes"], 2),
            ("Which of the following is supervised learning?", ["KMeans", "SVM", "DBSCAN", "Apriori"], 1),
            ("What is overfitting?", ["Model too simple", "Model fits training data too well", "Model under-trained", "None"], 1),
            ("Which function loads a CSV in pandas?", ["pd.load()", "pd.read_csv()", "pd.import()", "pd.get_csv()"], 1),
            ("Which chart is best for trend over time?", ["Pie", "Bar", "Line", "Scatter"], 2),
            ("What is the range of correlation coefficient?", ["-2 to 2", "0 to 1", "-1 to 1", "0 to ∞"], 2)
        ],
        "AI/ML Engineer": [
        ("What is gradient descent used for?", ["Optimization", "Classification", "Data Cleaning", "Visualization"], 0),
        ("Which library is used for deep learning?", ["Scikit-learn", "Matplotlib", "TensorFlow", "Pandas"], 2),
        ("Which activation function is most common in hidden layers?", ["Sigmoid", "ReLU", "Tanh", "Softmax"], 1),
        ("What is the goal of unsupervised learning?", ["Prediction", "Classification", "Clustering", "Regression"], 2),
        ("Which concept is used to avoid overfitting in ML?", ["Regularization", "Normalization", "Batching", "Gradient Clipping"], 0),
        ("Which file format is used to store trained models?", [".csv", ".json", ".pkl", ".html"], 2),
        ("What does RNN stand for?", ["Recursive Neural Network", "Reinforced Network Node", "Recurrent Neural Network", "Regularized Neural Net"], 2),
        ("What is the use of dropout in neural networks?", ["Accelerate learning", "Increase memory", "Prevent overfitting", "Add complexity"], 2),
        ("Which method is used to evaluate model performance on new data?", ["Training accuracy", "Test accuracy", "Cross entropy", "Mean absolute error"], 1),
        ("Which framework is used in production-ready ML systems?", ["TensorFlow", "Excel", "SAS", "MS Paint"], 0)
    ],
    "Cloud Engineer": [
        ("Which cloud model provides virtual machines?", ["IaaS", "PaaS", "SaaS", "NaaS"], 0),
        ("What does AWS EC2 stand for?", ["Elastic Cloud Compute", "External Cloud Compute", "Elastic Container Compute", "None"], 0),
        ("Which storage is object-based in AWS?", ["EBS", "EFS", "S3", "Glacier"], 2)
    ],
      "Web Developer": [
        ("What does HTML stand for?", ["Hyper Trainer Markup Language", "HyperText Markup Language", "Home Tool Markup Language", "Hyperlink and Text Markup"], 1),
        ("What does CSS stand for?", ["Colorful Style Sheets", "Cascading Style Sheets", "Computer Style Sheets", "Creative Style Sheets"], 1),
        ("Which tag is used to insert image in HTML?", ["<pic>", "<image>", "<img>", "<src>"], 2)
    ]
        # Add more roles if needed...
    }

    job_role = st.selectbox("Select the Job Role:", list(question_bank.keys()))

    if "quiz_started" not in st.session_state:
        st.session_state.quiz_started = False
        st.session_state.score = 0
        st.session_state.q_index = 0
        st.session_state.questions = []

    if st.button("Start Quiz"):
        st.session_state.quiz_started = True
        st.session_state.q_index = 0
        st.session_state.score = 0
        st.session_state.questions = random.sample(question_bank[job_role], min(10, len(question_bank[job_role])))

    if st.session_state.quiz_started and st.session_state.q_index < len(st.session_state.questions):
        q, options, correct = st.session_state.questions[st.session_state.q_index]
        st.subheader(f"Q{st.session_state.q_index + 1} of {len(st.session_state.questions)}")
        selected = st.radio(q, options, key=f"q{st.session_state.q_index}")

        if st.button("Next"):
            if options.index(selected) == correct:
                st.session_state.score += 1
            st.session_state.q_index += 1

    elif st.session_state.quiz_started and st.session_state.q_index >= len(st.session_state.questions):
        score = st.session_state.score
        total = len(st.session_state.questions)
        percent = round((score / total) * 100, 2)

        st.success(f"🎉 Quiz Done! Score: {score}/{total} ({percent}%)")
        if percent >= 75:
            st.balloons()
            st.info("✅ You're ready for this role!")
        else:
            st.warning("⚠️ Brush up a bit more before applying.")

        if st.button("Retake Quiz"):
            st.session_state.quiz_started = False

# ----------------- PAGE 2: ROADMAP ----------------- #
elif page == "📈 Roadmap Generator":
    st.title("🚀 AI Career Roadmap Generator")

    current_role = st.text_input("Current Role (e.g., Marketing Intern)")
    target_role = st.text_input("Target Role (e.g., Data Analyst)")
    timeframe = st.text_input("Timeframe (e.g., 6 months)")

    if st.button("Generate My Roadmap"):
        if not current_role or not target_role or not timeframe:
            st.warning("Please fill out all fields.")
        else:
            with st.spinner("Generating roadmap..."):
                prompt = f"""
                Generate a detailed, step-by-step career roadmap for transitioning from 
                {current_role} to {target_role} in {timeframe}.
                Include:
                1. Skills to learn (with free course links)
                2. Projects to build
                3. Job search strategies.
                Format as a numbered list with deadlines.
                """

                try:
                    client = openai.OpenAI(
                        api_key="sk-LMrDzMxd78EJxvT84EblDHgyEF9sO8m8eSrYw9Srf0jgeR2W",
                        base_url="https://api.chatanywhere.tech/v1"
                    )
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    roadmap = response.choices[0].message.content
                    st.success("Here’s your personalized roadmap:")
                    st.markdown(roadmap)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

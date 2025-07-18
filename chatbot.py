import streamlit as st
import openai
import random

# OpenAI client setup
client = openai.OpenAI(
    api_key="sk-LMrDzMxd78EJxvT84EblDHgyEF9sO8m8eSrYw9Srf0jgeR2W",
    base_url="https://api.chatanywhere.tech/v1"
)

# Empathy & Action messages
empathy_prompts = [
    "I'm really sorry you're feeling this way. You're not alone. Many successful people faced rejection early in their careers.",
    "It sounds like you're going through a tough time. Would you like to talk about what's been happening or see some quick tips to regroup?",
    "Rejections can be painful, but they're also learning opportunities. Let's explore ways to bounce back stronger."
]

action_suggestions = [
    "Would you like to review some resume tips?",
    "Want to try a quick mock interview to rebuild confidence?",
    "Would you like to explore short-term certifications to upskill?",
    "Would you like to read a success story from someone who overcame similar challenges?"
]

# Detect negative emotion
def detect_negative_emotion(user_input):
    negative_keywords = ['stuck', 'rejected', 'fail', 'giving up', 'lost', 'hopeless', 'depressed']
    return any(word in user_input.lower() for word in negative_keywords)

# Generate AI response
def generate_ai_response(messages):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Error]: {e}"

# Streamlit app setup
st.set_page_config(page_title="Career Crisis Assistant", page_icon="🧭")
st.title(" Career Crisis Assistant")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": "You are an empathetic career guidance coach who helps users navigate emotional career struggles with warmth, encouragement, and practical advice."}
    ]

# Chat container
chat_container = st.container()
input_container = st.container()

# Display chat history
with chat_container:
    st.markdown("### 💬 Conversation")
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        elif msg["role"] == "assistant":
            st.markdown(f"**Assistant:** {msg['content']}")

# Input form for new messages
with input_container:
    with st.form(key="user_input_form", clear_on_submit=True):
        user_input = st.text_input("Type your message here:", placeholder="I'm feeling stuck in my career...")
        submit_button = st.form_submit_button(label="Send")

# Handle new message
if submit_button and user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # If negative emotion detected, provide empathy + action
    if detect_negative_emotion(user_input):
        empathy = random.choice(empathy_prompts)
        action = random.choice(action_suggestions)
        st.session_state.chat_history.append({"role": "assistant", "content": empathy})
        st.session_state.chat_history.append({"role": "assistant", "content": action})

    # Then generate AI response
    ai_response = generate_ai_response(st.session_state.chat_history)
    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})

# Footer prompt
st.markdown("---")
st.info("💡 You can continue chatting by typing your next message above.")

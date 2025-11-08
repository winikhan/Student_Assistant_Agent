import os
import streamlit as st
from dotenv import load_dotenv
from litellm import completion
import re

# ✅ Load Environment Variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# ✅ Streamlit Page Config
st.set_page_config(page_title="Student Assistant Agent", page_icon="🚀", layout="wide")

# ------------------ SESSION STATE SETUP ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "history" not in st.session_state:
    st.session_state.history = {}

# ------------------ CUSTOM CSS ------------------
st.markdown("""
    <style>
        body, .stApp {
            background-color: #f8f9fb;
            font-family: 'Poppins', sans-serif;
        }
        .stChatMessage {
            border-radius: 12px;
            padding: 10px 16px;
            margin-bottom: 8px;
        }
        .stChatMessage[data-testid="stChatMessage-user"] {
            background-color: #DCF8C6;
            text-align: right;
        }
        .stChatMessage[data-testid="stChatMessage-assistant"] {
            background-color: #ffffff;
            border: 1px solid #e5e5e5;
        }
        [data-testid="stSidebar"] {
            background-color: #2c2f38;
            color: white;
        }
        [data-testid="stSidebar"] h2, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
            color: white !important;
        }
        .stButton>button {
            border-radius: 10px;
            background-color: #4CAF50;
            color: white;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------ SIDEBAR ------------------
with st.sidebar:
    st.title("🎓 Student Assistant")
    st.markdown("---")

    if not st.session_state.logged_in:
        st.subheader("🔐 Login / Sign Up")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login"):
                if username and password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    if username not in st.session_state.history:
                        st.session_state.history[username] = []
                    st.success(f"Welcome back, {username}!")
                else:
                    st.error("Please enter username & password.")
        with col2:
            if st.button("Sign Up"):
                if username and password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.history[username] = []
                    st.success(f"Account created! Welcome {username}")
                else:
                    st.error("Please fill in all fields.")
    else:
        st.markdown(f"👋 **Hello, {st.session_state.username}!**")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.messages = []

        st.markdown("---")
        st.subheader("🕒 Chat History")

        if st.session_state.username in st.session_state.history:
            user_history = st.session_state.history[st.session_state.username]
            if len(user_history) == 0:
                st.info("No chats yet.")
        st.markdown("---")
        if st.button("➕ New Chat"):
            st.session_state.messages = []

# ------------------ MAIN CHAT INTERFACE ------------------
st.title("🚀 Student Assistant Agent")
st.write("Your personal AI-powered study companion using **Gemini API**")

# Dropdown for mode selection
mode = st.selectbox("📚 What do you want help with?", [
    "❓ Ask a Question",
    "🧠 Explain a Topic",
    "📝 Summarize Text",
    "📅 Get a Study Plan",
    "💡 Get Motivation"
])

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ------------------ EDUCATION FILTER FUNCTION ------------------
def is_educational_query(text):
    """
    Check if the query is related to educational topics.
    """
    education_keywords = [
        "study", "learn", "subject", "exam", "physics", "chemistry", "math", "biology",
        "history", "notes", "explanation", "education", "assignment", "topic", "summarize",
        "plan", "science", "programming", "python", "cpp", "java", "project", "report",
        "motivation", "university", "school", "college"
    ]
    return any(re.search(rf"\\b{k}\\b", text.lower()) for k in education_keywords)

# ------------------ USER INPUT ------------------
if st.session_state.logged_in:
    user_input = st.chat_input("Type your message here...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # 🔒 Restriction: only reply to educational queries
        if not is_educational_query(user_input):
            restricted_msg = (
                "📘 **I'm your Student Study Agent.**\n\n"
                "I can only assist with educational and academic queries such as:\n"
                "- Explaining study topics\n"
                "- Helping with assignments\n"
                "- Summarizing notes\n"
                "- Creating study plans\n"
                "- Providing exam motivation\n\n"
                "Please ask something related to your studies. 😊"
            )
            with st.chat_message("assistant"):
                st.markdown(restricted_msg)
            st.session_state.messages.append({"role": "assistant", "content": restricted_msg})

        else:
            # Normal response for study-related content
            if mode.startswith("❓"):
                prompt = f"Answer this clearly for students: {user_input}"
            elif mode.startswith("🧠"):
                prompt = f"Explain this topic for a beginner student: {user_input}"
            elif mode.startswith("📝"):
                prompt = f"Summarize this educational text into bullet points: {user_input}"
            elif mode.startswith("📅"):
                prompt = f"Make a 7-day study plan for: {user_input}"
            elif mode.startswith("💡"):
                prompt = f"Give a motivational study tip for this situation: {user_input}"
            else:
                prompt = user_input

            try:
                response = completion(
                    model="gemini/gemini-2.0-flash",
                    messages=[{"role": "user", "content": prompt}],
                    api_key=api_key
                )
                reply = response["choices"][0]["message"]["content"]
                with st.chat_message("assistant"):
                    st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

            except Exception as e:
                st.error(f"⚠️ Error from Gemini: {str(e)}")
else:
    st.warning("Please login to start chatting.")

# ------------------ FOOTER ------------------
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:gray;'>Made with ❤️ by <b>@Waniza Khan</b> | © 2025 All rights reserved.</p>",
    unsafe_allow_html=True
)

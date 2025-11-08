import os
import streamlit as st
from dotenv import load_dotenv
from litellm import completion

# ✅ Load Environment Variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# ✅ Streamlit Page Config
st.set_page_config(page_title="Student Assistant Agent", page_icon="🚀", layout="wide")

# ------------------ SESSION STATE ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "history" not in st.session_state:
    st.session_state.history = {}

# ------------------ DARK MODE STYLING ------------------
st.markdown("""
    <style>
        body, .stApp { background-color: #0e1117; color: #e5e5e5; font-family: 'Poppins', sans-serif; }
        .stChatMessage { border-radius: 12px; padding: 10px 16px; margin-bottom: 8px; }
        .stChatMessage[data-testid="stChatMessage-user"] { background-color: #1f2937; text-align: right; color: #e5e5e5; }
        .stChatMessage[data-testid="stChatMessage-assistant"] { background-color: #2a2f3b; border: 1px solid #333; color: #dcdcdc; }
        [data-testid="stSidebar"] { background-color: #1a1d23; color: white; }
        [data-testid="stSidebar"] h2, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: #f8f9fa !important; }
        .stSelectbox div[data-baseweb="select"] > div { background-color: #1f2937; color: #f1f1f1; }
        .stTextInput input, .stPasswordInput input { background-color: #1f2937; color: #e5e5e5; border: 1px solid #333; border-radius: 8px; }
        .stButton>button { border-radius: 10px; background-color: #4CAF50; color: white; font-weight: 600; }
        .stButton>button:hover { background-color: #45a049; }
        footer {visibility: hidden;}
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
st.write("💡 Your personal **AI-powered study companion** using Gemini API")

# Dropdown for mode selection
mode = st.selectbox("📚 What do you want help with?", [
    "❓ Ask a Question",
    "🧠 Explain a Topic",
    "📝 Summarize Text",
    "📅 Get a Study Plan",
    "💡 Get Motivation"
])

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ------------------ USER INPUT ------------------
if st.session_state.logged_in:
    user_input = st.chat_input("💬 Type your message here...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Directly send to Gemini API
        if mode.startswith("❓"):
            prompt = f"Answer clearly for a student: {user_input}"
        elif mode.startswith("🧠"):
            prompt = f"Explain this topic simply for a beginner student: {user_input}"
        elif mode.startswith("📝"):
            prompt = f"Summarize this educational text into bullet points: {user_input}"
        elif mode.startswith("📅"):
            prompt = f"Make a 7-day study plan for: {user_input}"
        elif mode.startswith("💡"):
            prompt = f"Give a motivational study tip about: {user_input}"
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
    st.warning("🔐 Please login to start chatting.")

# ------------------ FOOTER ------------------
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#8b949e;'>Made with ❤️ by <b>@Waniza Khan</b> | © 2025 All rights reserved.</p>",
    unsafe_allow_html=True
)

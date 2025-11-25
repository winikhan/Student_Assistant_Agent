import os
import streamlit as st
from dotenv import load_dotenv
from litellm import completion

# ✅ Load Environment Variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Streamlit Page Config
st.set_page_config(page_title="Student Assistant", layout="centered")

# ------------------ SESSION STATE ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "history" not in st.session_state:
    st.session_state.history = {}
if "mode" not in st.session_state:
    st.session_state.mode = "login"  # login/signup toggle

# ------------------ STYLING ------------------
st.markdown("""
<style>
body, .stApp { background-color: #f0f2f5; font-family: 'Helvetica Neue', sans-serif; }
.stChatMessage { border-radius: 12px; padding: 10px 16px; margin-bottom: 8px; }
.stChatMessage[data-testid="stChatMessage-user"] { background-color: #1f2937; text-align: right; color: #e5e5e5; }
.stChatMessage[data-testid="stChatMessage-assistant"] { background-color: #2a2f3b; border: 1px solid #333; color: #dcdcdc; }
.login-container { display: flex; justify-content: center; align-items: center; height: 100vh; }
.login-box { width: 360px; background-color: #fff; padding: 40px 30px; border-radius: 12px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }
.login-box h2 { text-align: center; margin-bottom: 30px; font-weight: 600; color: #333; }
.stTextInput>div>div>input { height: 40px !important; font-size: 14px !important; padding: 0 10px !important; }
.stButton>button { width: 100%; padding: 10px 0 !important; background-color: #1877f2; color: white; font-size: 16px; border-radius: 6px; font-weight: 600; }
.stButton>button:hover { background-color: #166fe5; }
.toggle-box { text-align: center; margin-top: 20px; font-size: 14px; color: #555; }
.toggle-box button { background: none; border: none; color: #1877f2; font-weight: 600; cursor: pointer; }
</style>
""", unsafe_allow_html=True)

# ------------------ LOGIN / SIGNUP SCREEN ------------------
if not st.session_state.logged_in:
    st.markdown('<div class="login-container"><div class="login-box">', unsafe_allow_html=True)

    st.markdown(f"## {'Login' if st.session_state.mode=='login' else 'Sign Up'}", unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            if username and password:
                # Simple in-memory login
                if username in st.session_state.history:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.messages = st.session_state.history[username]
                    st.success(f"Welcome back, {username}!")
                else:
                    st.error("User not found. Try Sign Up.")
            else:
                st.error("Please enter username & password.")
    with col2:
        if st.button("Sign Up"):
            if username and password:
                if username not in st.session_state.history:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.messages = []
                    st.session_state.history[username] = []
                    st.success(f"Account created! Welcome {username}")
                else:
                    st.error("Username already exists.")
            else:
                st.error("Please fill in all fields.")

    # Toggle login/signup
    if st.button("Switch to " + ("Sign Up" if st.session_state.mode=="login" else "Login")):
        st.session_state.mode = "signup" if st.session_state.mode=="login" else "login"

    st.markdown('</div></div>', unsafe_allow_html=True)

# ------------------ MAIN CHAT INTERFACE ------------------
else:
    # Sidebar for history & logout
    with st.sidebar:
        st.markdown(f"👋 **Hello, {st.session_state.username}!**")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.messages = []

        st.markdown("---")
        st.subheader("🕒 Chat History")
        if st.session_state.messages:
            for chat in st.session_state.messages[-20:]:
                st.markdown(f"- **{chat['role'].capitalize()}**: {chat['content']}")
        else:
            st.info("No chats yet.")
        st.markdown("---")
        if st.button("➕ New Chat"):
            st.session_state.messages = []

    st.title("🚀 Student Assistant Agent")
    st.write("💡 Your personal **AI-powered study companion** using Gemini API")

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

    # User input
    user_input = st.chat_input("💬 Type your message here...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.history[st.session_state.username] = st.session_state.messages.copy()
        with st.chat_message("user"):
            st.markdown(user_input)

        # Prepare prompt based on mode
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
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.session_state.history[st.session_state.username] = st.session_state.messages.copy()
            with st.chat_message("assistant"):
                st.markdown(reply)

        except Exception as e:
            st.error(f"⚠️ Error from Gemini: {str(e)}")

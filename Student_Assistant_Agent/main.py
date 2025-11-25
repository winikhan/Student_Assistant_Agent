import os
import mysql.connector
import streamlit as st
from dotenv import load_dotenv
from litellm import completion
from datetime import datetime

# ✅ Load Environment Variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# MySQL Connection
conn = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST", "localhost"),
    user=os.getenv("MYSQL_USER", "root"),
    password=os.getenv("MYSQL_PASSWORD", ""),
    database=os.getenv("MYSQL_DB", "student_assistant")
)
cursor = conn.cursor()

# Create tables if not exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS chat_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    role VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
""")

conn.commit()

# ------------------ SESSION STATE ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None

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
.login-container { display: flex; flex-direction: column; justify-content: center; align-items: center; height: 90vh; }
.login-box { background-color: #1a1d23; padding: 40px; border-radius: 12px; box-shadow: 0px 0px 20px rgba(0,0,0,0.5); }
</style>
""", unsafe_allow_html=True)

# ------------------ LOGIN / SIGNUP SCREEN ------------------
if not st.session_state.logged_in:
    st.markdown('<div class="login-container"><div class="login-box">', unsafe_allow_html=True)
    st.markdown("## 🔐 Login / Sign Up", unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            if username and password:
                cursor.execute("SELECT id FROM users WHERE username=%s AND password=%s", (username, password))
                result = cursor.fetchone()
                if result:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.user_id = result[0]
                    # Load previous chat messages
                    cursor.execute("SELECT role, message FROM chat_history WHERE user_id=%s ORDER BY id ASC", (st.session_state.user_id,))
                    messages = cursor.fetchall()
                    st.session_state.messages = [{"role": role, "content": msg} for role, msg in messages]
                    st.success(f"Welcome back, {username}!")
                else:
                    st.error("Invalid username or password.")
            else:
                st.error("Please enter username & password.")
    with col2:
        if st.button("Sign Up"):
            if username and password:
                try:
                    cursor.execute("INSERT INTO users (username, password) VALUES (%s,%s)", (username, password))
                    conn.commit()
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.user_id = cursor.lastrowid
                    st.session_state.messages = []
                    st.success(f"Account created! Welcome {username}")
                except mysql.connector.Error as e:
                    st.error("Username already exists.")
            else:
                st.error("Please fill in all fields.")

    st.markdown('</div></div>', unsafe_allow_html=True)

# ------------------ MAIN APP AFTER LOGIN ------------------
else:
    # Sidebar for history and logout
    with st.sidebar:
        st.markdown(f"👋 **Hello, {st.session_state.username}!**")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.user_id = None
            st.session_state.messages = []

        st.markdown("---")
        st.subheader("🕒 Chat History")
        if st.session_state.messages:
            for chat in st.session_state.messages[-20:]:  # show last 20 messages
                st.markdown(f"- {chat['role'].capitalize()}: {chat['content']}")
        else:
            st.info("No chats yet.")
        st.markdown("---")
        if st.button("➕ New Chat"):
            st.session_state.messages = []

    # Main Chat Interface
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
        cursor.execute(
            "INSERT INTO chat_history (user_id, role, message) VALUES (%s,%s,%s)",
            (st.session_state.user_id, "user", user_input)
        )
        conn.commit()
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
            cursor.execute(
                "INSERT INTO chat_history (user_id, role, message) VALUES (%s,%s,%s)",
                (st.session_state.user_id, "assistant", reply)
            )
            conn.commit()
            with st.chat_message("assistant"):
                st.markdown(reply)

        except Exception as e:
            st.error(f"⚠️ Error from Gemini: {str(e)}")

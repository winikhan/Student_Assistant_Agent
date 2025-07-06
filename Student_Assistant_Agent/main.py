import os
import streamlit as st
from dotenv import load_dotenv
from litellm import completion, _turn_on_debug

# ✅ Step 1: Load Environment Variables
load_dotenv()

# ✅ Step 2: Streamlit Page Config
st.set_page_config(page_title="Student Assistant Agent", page_icon="🚀", layout="wide")
st.title("🚀 Student Assistant Agent")
st.write("Your AI-powered study companion using Gemini API")

# ✅ Step 3: Get Gemini API Key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("❌ Please set a valid GEMINI_API_KEY in your .env file.")
    st.stop()

# ✅ Step 4: Mode Selection Dropdown
mode = st.selectbox("📚 What do you want help with?", [
    "❓ Ask a Question",
    "🧠 Explain a Topic",
    "📝 Summarize Text",
    "📅 Get a Study Plan",
    "💡 Get Motivation"
])

# ✅ Step 5: User Chat Input
user_input = st.chat_input("Hey, how can I help you today?")

# ✅ Step 6: Process Input & Call Gemini
if user_input:
    # Show user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # 🎯 Step 7 - Prompt Design
    if mode.startswith("❓"):
        prompt = f"Answer this clearly: {user_input}"
    elif mode.startswith("🧠"):
        prompt = f"Explain this like I'm a beginner: {user_input}"
    elif mode.startswith("📝"):
        prompt = f"Summarize this text into bullet points: {user_input}"
    elif mode.startswith("📅"):
        prompt = f"Make a 7-day study plan for: {user_input}"
    elif mode.startswith("💡"):
        prompt = f"Give a motivational tip for this scenario: {user_input}"
    else:
        prompt = user_input  # fallback

    try:
        # ✅ Gemini API Call
        response = completion(
            model="gemini/gemini-2.0-flash",
            messages=[{"role": "user", "content": prompt}],
            api_key=api_key
        )
        reply = response["choices"][0]["message"]["content"]

        # ✅ Show assistant reply
        with st.chat_message("assistant"):
            st.markdown(reply)

    except Exception as e:
        st.error(f"⚠️ Error from Gemini: {str(e)}")

    # ✅ Footer shown AFTER assistant message
    st.markdown("---")
    st.markdown("Made with ❤️ by **@Waniza Khan** | © 2025 All rights reserved.")

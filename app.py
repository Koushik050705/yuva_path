import streamlit as st
import speech_recognition as sr
import pyttsx3
from langdetect import detect

st.set_page_config(page_title="YuvaPath - AI Career Co-Pilot", layout="centered")
st.title("🎯 YuvaPath: AI Career Co-Pilot")
st.markdown("#### Personalized career guidance for every Indian youth")

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Career guidance mapping
career_paths = {
    "BA": ["Content Writer", "UPSC Aspirant", "Marketing Analyst"],
    "BSC": ["Data Analyst", "Lab Technician", "UX Designer"],
    "BCOM": ["Accountant", "Financial Analyst", "Entrepreneur"],
    "OTHER": ["Skill-based jobs", "Certifications", "Freelancing"]
}

def get_speech_input(prompt_text):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info(prompt_text)
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            st.error("Could not understand audio.")
        except sr.RequestError:
            st.error("Could not request results; check your internet.")
    return ""

# --- UI Input ---
st.markdown("##### 🎤 Speak or type your input")

col1, col2 = st.columns(2)

with col1:
    if st.button("🎙 Speak Degree"):
        degree = get_speech_input("Speak your degree (e.g., BA, BSc, BCom)")
    else:
        degree = st.text_input("📚 Degree (e.g., BA, BSc, BCom)")

with col2:
    if st.button("🎙 Speak Language"):
        language = get_speech_input("Speak your preferred language")
    else:
        language = st.text_input("🗣 Preferred Language (e.g., English, Hindi)")

# --- Process ---
if st.button("🚀 Get Career Guidance"):
    degree_upper = degree.strip().upper()
    paths = career_paths.get(degree_upper, career_paths["OTHER"])
    roadmap = f"As a {degree} graduate, focus on soft skills, free certifications, and industry tools."

    st.success("✅ Personalized Career Recommendations")
    for i, path in enumerate(paths, 1):
        st.markdown(f"**{i}. {path}**")

    st.info(f"📍 Learning Roadmap:\n{roadmap}")

    try:
        lang_detected = detect(degree)
        st.markdown(f"🌐 Language Detected from Input: `{lang_detected}`")
    except:
        st.markdown("🌐 Language detection failed.")

    # TTS Button
    if st.button("🔊 Speak Roadmap"):
        engine.say(roadmap)
        engine.runAndWait()

import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import speech_recognition as sr
import pyttsx3
from langdetect import detect
import av
import queue
import numpy as np
import tempfile
import wave

st.set_page_config(page_title="YuvaPath - Career Co-Pilot", layout="centered")

st.title("🎯 YuvaPath: AI Career Co-Pilot")
st.markdown("#### Personalized career guidance with voice or text")

# TTS Engine
engine = pyttsx3.init()
engine.setProperty("rate", 150)

career_paths = {
    "BA": ["Content Writer", "UPSC Aspirant", "Marketing Analyst"],
    "BSC": ["Data Analyst", "Lab Technician", "UX Designer"],
    "BCOM": ["Accountant", "Financial Analyst", "Entrepreneur"],
    "OTHER": ["Skill-based jobs", "Certifications", "Freelancing"]
}

# Set up audio recording
audio_queue = queue.Queue()

class AudioProcessor:
    def __init__(self) -> None:
        self.recording = False

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio = frame.to_ndarray().flatten().astype(np.float32)
        audio_queue.put(audio)
        return frame

st.markdown("### 🎙️ Voice Input (speak your degree)")

ctx = webrtc_streamer(
    key="example",
    mode=WebRtcMode.SENDONLY,
    in_audio=True,
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio": True, "video": False},
)

degree = ""

if st.button("📝 Transcribe Voice"):
    if not audio_queue.empty():
        st.info("Transcribing...")

        # Save audio to temp WAV
        audio_data = np.concatenate(list(audio_queue.queue))
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            with wave.open(f.name, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(16000)
                wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())
            audio_path = f.name

        # Transcribe using SpeechRecognition
        r = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = r.record(source)
            try:
                degree = r.recognize_google(audio)
                st.success(f"🎤 You said: {degree}")
            except sr.UnknownValueError:
                st.warning("Could not understand audio.")
            except sr.RequestError:
                st.error("Speech Recognition API error.")
    else:
        st.warning("No voice captured yet.")

# Manual fallback input
degree_input = st.text_input("📚 Or type your Degree", value=degree)
language = st.selectbox("🌐 Preferred Language", ["English", "Hindi", "Tamil", "Telugu"])

if st.button("🚀 Get Career Guidance"):
    degree_upper = degree_input.strip().upper()
    paths = career_paths.get(degree_upper, career_paths["OTHER"])
    roadmap = f"As a {degree_input}, focus on learning communication, digital tools, and explore {paths[0]}."

    st.success("✅ Career Recommendations")
    for i, path in enumerate(paths, 1):
        st.markdown(f"**{i}. {path}**")

    try:
        lang_detected = detect(degree_input)
        st.caption(f"🌐 Language Detected: `{lang_detected}`")
    except:
        st.caption("🌐 Language detection failed.")

    if st.button("🔊 Speak Roadmap"):
        engine.say(roadmap)
        engine.runAndWait()

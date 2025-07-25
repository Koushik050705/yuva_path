import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import pyttsx3
from langdetect import detect
import queue
import av
import whisper

# Initialize Whisper ASR model (small or base for faster performance)
model = whisper.load_model("base")

st.set_page_config(page_title="YuvaPath", layout="centered")
st.title("🎯 YuvaPath: AI Career Co-Pilot")
st.markdown("#### Personalized career guidance with voice or text")

# Queue to hold audio frames
audio_queue = queue.Queue()

class AudioProcessor(AudioProcessorBase):
    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio_queue.put(frame.to_ndarray().flatten())
        return frame

# TTS setup
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Simple career database
career_paths = {
    "BA": ["Content Writer", "UPSC Aspirant", "Marketing Analyst"],
    "BSC": ["Data Analyst", "Lab Technician", "UX Designer"],
    "BCOM": ["Accountant", "Financial Analyst", "Entrepreneur"],
    "OTHER": ["Skill-based jobs", "Certifications", "Freelancing"]
}

# --- Speech Recording Section ---
st.markdown("### 🎙️ Speak or Type Your Degree")
speech_mode = st.toggle("Use Voice Input", value=False)

degree = ""

if speech_mode:
    webrtc_streamer(key="voice", audio_processor_factory=AudioProcessor)

    if st.button("📝 Transcribe Voice"):
        with st.spinner("Transcribing..."):
            import numpy as np
            import soundfile as sf

            audio_data = []

            # Collect audio from queue
            while not audio_queue.empty():
                audio_data.append(audio_queue.get())

            if audio_data:
                audio_np = np.concatenate(audio_data).astype(np.float32)
                sf.write("temp.wav", audio_np, samplerate=16000)
                result = model.transcribe("temp.wav")
                degree = result["text"]
                st.success(f"You said: {degree}")
            else:
                st.warning("No audio captured yet.")
else:
    degree = st.text_input("📚 Enter Your Degree (e.g., BA, BSc, BCom)")

language = st.selectbox("🗣 Preferred Language", ["English", "Hindi", "Tamil", "Telugu"])

# --- Career Recommendation Logic ---
if st.button("🚀 Get Career Guidance"):
    degree_upper = degree.strip().upper()
    paths = career_paths.get(degree_upper, career_paths["OTHER"])
    roadmap = f"As a {degree}, you can grow by learning communication, digital tools, and exploring {paths[0]}."

    st.success("✅ Career Recommendations")
    for i, path in enumerate(paths, 1):
        st.markdown(f"**{i}. {path}**")

    st.info(f"📍 Learning Roadmap: {roadmap}")

    try:
        lang_detected = detect(degree)
        st.caption(f"🌐 Detected Input Language: `{lang_detected}`")
    except:
        st.caption("🌐 Language detection failed.")

    if st.button("🔊 Speak Roadmap"):
        engine.say(roadmap)
        engine.runAndWait()

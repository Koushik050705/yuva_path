import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import speech_recognition as sr
import langdetect
from gtts import gTTS
import numpy as np
import av
import wave
import tempfile
import queue
import base64

# Config
st.set_page_config(page_title="YuvaPath - Career Co-Pilot", layout="centered")
st.title("🎯 YuvaPath: AI Career Co-Pilot")
st.markdown("#### Personalized career guidance with voice or text")

# Simple career path database
career_paths = {
    "BA": ["Content Writer", "UPSC Aspirant", "Marketing Analyst"],
    "BSC": ["Data Analyst", "Lab Technician", "UX Designer"],
    "BCOM": ["Accountant", "Financial Analyst", "Entrepreneur"],
    "OTHER": ["Skill-based jobs", "Certifications", "Freelancing"]
}

# Audio queue setup
audio_queue = queue.Queue()

class AudioProcessor:
    def __init__(self) -> None:
        pass

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio = frame.to_ndarray().flatten().astype(np.float32)
        audio_queue.put(audio)
        return frame

# gTTS text-to-speech
def speak_text(text):
    tts = gTTS(text=text, lang="en")
    tts.save("roadmap.mp3")
    with open("roadmap.mp3", "rb") as f:
        audio_bytes = f.read()
        b64 = base64.b64encode(audio_bytes).decode()
        audio_html = f"""
        <audio autoplay controls>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

# Voice input section
st.subheader("🎙️ Speak or Type Your Degree")
degree = ""
use_voice = st.toggle("Use Microphone Input")

if use_voice:
    webrtc_ctx = webrtc_streamer(
        key="speech",
        mode=WebRtcMode.SENDONLY,
        in_audio=True,
        audio_processor_factory=AudioProcessor,
        media_stream_constraints={"audio": True, "video": False},
    )

    if st.button("📝 Transcribe Voice"):
        if not audio_queue.empty():
            st.info("Transcribing...")
            audio_data = np.concatenate(list(audio_queue.queue))

            # Save audio to temp WAV file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                with wave.open(f.name, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(16000)
                    wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())
                audio_path = f.name

            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_path) as source:
                audio = recognizer.record(source)
                try:
                    degree = recognizer.recognize_google(audio)
                    st.success(f"🎤 You said: {degree}")
                except sr.UnknownValueError:
                    st.warning("Couldn't understand the audio.")
                except sr.RequestError:
                    st.error("Speech recognition failed. Try again.")
        else:
            st.warning("No audio received. Try speaking after mic starts.")

# Manual input fallback
degree_input = st.text_input("📚 Or type your Degree", value=degree)
language = st.selectbox("🌐 Preferred Language", ["English", "Hindi", "Tamil", "Telugu"])

# Main career logic
if st.button("🚀 Get Career Guidance"):
    degree_upper = degree_input.strip().upper()
    paths = career_paths.get(degree_upper, career_paths["OTHER"])
    roadmap = f"As a {degree_input}, focus on improving communication, learning digital tools, and explore a path like {paths[0]}."

    st.success("✅ Career Recommendations")
    for i, path in enumerate(paths, 1):
        st.markdown(f"**{i}. {path}**")

    try:
        detected_lang = langdetect.detect(degree_input)
        st.caption(f"🌐 Detected Input Language: `{detected_lang}`")
    except:
        st.caption("🌐 Language detection failed.")

    if st.button("🔊 Speak Roadmap"):
        speak_text(roadmap)

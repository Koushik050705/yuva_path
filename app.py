import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import speech_recognition as sr
from gtts import gTTS
import langdetect
import numpy as np
import av
import wave
import tempfile
import queue
import base64

st.set_page_config(page_title="YuvaPath - AI Career Co-Pilot", layout="centered")
st.title("🎯 YuvaPath: AI Career Co-Pilot")
st.markdown("#### Personalized career guidance with voice or text")

# ---------------- Career Paths -------------------
career_paths = {
    "BA": ["Content Writer", "UPSC Aspirant", "Marketing Analyst"],
    "BSC": ["Data Analyst", "Lab Technician", "UX Designer"],
    "BCOM": ["Accountant", "Financial Analyst", "Entrepreneur"],
    "BTECH": ["Software Developer", "ML Engineer", "Startup Founder"],
    "BE": ["Civil Engineer", "Electrical Engineer", "Software Engineer"],
    "BCA": ["Web Developer", "Software Tester", "Python Developer"],
    "MCA": ["Full Stack Developer", "Data Scientist", "AI Specialist"],
    "MBA": ["Business Analyst", "Product Manager", "Marketing Executive"],
    "LLB": ["Lawyer", "Legal Advisor", "Judicial Services"],
    "DIPLOMA": ["Electrician", "Mechanical Technician", "Draftsman"],
    "BPHARMA": ["Pharmacist", "Clinical Researcher", "Medical Sales"],
    "MBBS": ["Doctor", "Medical Officer", "Public Health Expert"],
    "12TH": ["Intern", "Online Cert Courses", "Freelancer"],
    "10TH": ["Apprentice", "Online Cert Courses", "Startup Assistant"],
    "OTHER": ["Skill-based jobs", "Certifications", "Freelancing"]
}

# ---------------- Degree Normalization -------------------
def normalize_degree(degree_raw):
    degree = degree_raw.strip().upper()
    mappings = {
        "BACHELOR OF ARTS": "BA",
        "BACHELOR OF SCIENCE": "BSC",
        "BACHELOR OF COMMERCE": "BCOM",
        "BACHELOR OF TECHNOLOGY": "BTECH",
        "ENGINEERING": "BE",
        "COMPUTER APPLICATION": "BCA",
        "MASTER OF COMPUTER APPLICATION": "MCA",
        "MASTER OF BUSINESS ADMINISTRATION": "MBA",
        "LAW": "LLB",
        "LL.B": "LLB",
        "LLB": "LLB",
        "DIPLOMA": "DIPLOMA",
        "PHARMACY": "BPHARMA",
        "BPHARM": "BPHARMA",
        "MBBS": "MBBS",
        "12": "12TH",
        "12TH": "12TH",
        "10": "10TH",
        "10TH": "10TH"
    }
    for key in mappings:
        if key in degree:
            return mappings[key]
    return degree  # fallback

# ---------------- gTTS Speech Output -------------------
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

# ---------------- Voice Input (WebRTC) -------------------
audio_queue = queue.Queue()

class AudioProcessor:
    def __init__(self) -> None:
        pass

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio = frame.to_ndarray().flatten().astype(np.float32)
        audio_queue.put(audio)
        return frame

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
                    st.warning("Could not understand audio.")
                except sr.RequestError:
                    st.error("Speech Recognition error. Try again.")
        else:
            st.warning("No audio captured yet.")

# Manual text input fallback
degree_input = st.text_input("📚 Or type your Degree", value=degree)
language = st.selectbox("🌐 Preferred Language", ["English", "Hindi", "Tamil", "Telugu"])

# ---------------- Career Suggestion Output -------------------
if st.button("🚀 Get Career Guidance"):
    normalized_degree = normalize_degree(degree_input)
    paths = career_paths.get(normalized_degree, career_paths["OTHER"])
    roadmap = f"As a {degree_input}, focus on communication, digital tools, and explore {paths[0]}."

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

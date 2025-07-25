import streamlit as st
from gtts import gTTS
from io import BytesIO
import base64

# ------------------------ Career Data ------------------------ #
CAREER_DB = {
    "B.Tech": {
        "Software Engineer": ["Learn C/C++, Java or Python", "Data Structures and Algorithms", "Web Development / App Development", "Work on projects", "Prepare for interviews"],
        "Data Scientist": ["Python, Statistics, Probability", "Pandas, Numpy, Matplotlib", "Machine Learning", "Deep Learning", "Build portfolio projects"],
        "Mechanical Engineer": ["Thermodynamics", "Solid Mechanics", "CAD Software", "Industrial Training", "GATE Exam (optional)"]
    },
    "B.Sc": {
        "Research Scientist": ["Choose a domain: Physics, Chemistry, etc.", "Do MSc and focus on research", "Publish papers", "Apply for PhD"],
        "Lab Technician": ["Specialize in practical skills", "Do certifications", "Intern at labs/hospitals"],
        "Data Analyst": ["Learn Excel, Python/R", "Data Visualization (PowerBI/Tableau)", "SQL and Statistics"]
    },
    "B.Com": {
        "Chartered Accountant": ["Register with ICAI", "Clear CA Foundation", "Clear CA Inter and Final", "3 years Articleship"],
        "Financial Analyst": ["Learn Excel, Accounting, Financial Modeling", "Do CFA/FRM Certification", "Get internship at finance firms"],
        "Bank PO": ["Prepare for IBPS/SBI PO Exams", "Practice Quant, Reasoning, English"]
    },
    "BA": {
        "Civil Services (IAS/IPS)": ["Prepare for UPSC", "Read NCERTs", "Join coaching (optional)", "Practice essays, current affairs"],
        "Journalist": ["Do MA Journalism", "Work at a media house", "Build portfolio"],
        "Teacher": ["Do B.Ed", "Prepare for TET/CTET"]
    },
    "Law": {
        "Corporate Lawyer": ["Do internships at law firms", "Specialize in corporate law", "Clear bar exam"],
        "Litigation Lawyer": ["Practice under a senior", "Appear in court", "Focus on criminal/civil law"],
        "Legal Advisor": ["Work with companies or govt", "Offer compliance/legal advice"]
    },
    "MBBS": {
        "Doctor (Specialist)": ["Clear NEET PG", "Choose specialization: MD/MS", "Do residency"],
        "Hospital Administrator": ["Do MBA in Hospital Mgmt", "Work in hospital operations"],
        "Medical Researcher": ["Join ICMR, CSIR projects", "Publish research papers"]
    },
    "Diploma": {
        "Technician": ["Get certified", "Work in private/public sector"],
        "Junior Engineer": ["Prepare for SSC JE", "Work in govt/private projects"],
        "Freelancer": ["Do skill training: Electrician, Plumber, AutoCAD, etc."]
    },
    "Vocational": {
        "Digital Marketer": ["Learn SEO, SEM, Social Media", "Freelance or join firm"],
        "Fashion Designer": ["Do diploma", "Create portfolio", "Join brand or freelance"],
        "Animator": ["Learn Blender/AfterEffects", "Work on animated content"]
    }
}

# ------------------------ UI Layout ------------------------ #
st.set_page_config(page_title="YuvaPath: Career Guide", layout="centered")
st.title("🎓 YuvaPath - Voice-enabled AI Career Guide")

st.markdown("#### 👋 Hello! I’m your career assistant. Tell me a few things and I’ll suggest the best path for you.")

col1, col2 = st.columns(2)
qualification = col1.selectbox("Select your highest qualification", list(CAREER_DB.keys()))
interest = col2.text_input("Enter your interest or subject area (e.g., coding, design, law, business)", "")

language = st.selectbox("Preferred output language", ["English", "Telugu"])
submit = st.button("🔍 Show Career Path")

# ------------------------ Recommendation Logic ------------------------ #
def generate_roadmap(qualification, interest):
    options = CAREER_DB.get(qualification, {})
    matched = []
    for career, steps in options.items():
        if interest.lower() in career.lower() or interest.lower() in " ".join(steps).lower():
            matched.append((career, steps))
    if not matched:
        matched = list(options.items())[:2]  # Show top 2 if no match
    return matched

def text_to_speech(text, lang='en'):
    tts = gTTS(text=text, lang=lang)
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return mp3_fp

# ------------------------ Output ------------------------ #
if submit:
    st.subheader("📌 Recommended Careers and Roadmap:")
    results = generate_roadmap(qualification, interest)
    full_roadmap = ""

    for title, steps in results:
        st.markdown(f"**🎯 {title}**")
        for i, step in enumerate(steps, 1):
            st.markdown(f"- Step {i}: {step}")
            full_roadmap += f"Step {i}: {step}. "
        st.markdown("---")

    # Text-to-Speech
    st.subheader("🔊 Listen to Your Roadmap")
    lang_code = 'te' if language == "Telugu" else 'en'
    audio = text_to_speech(full_roadmap, lang=lang_code)
    b64 = base64.b64encode(audio.read()).decode()
    audio_html = f"""
        <audio autoplay controls>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

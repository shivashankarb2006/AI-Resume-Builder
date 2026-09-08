"""
AI Resume Builder - Main Application Entry Point
Phase 2: Comprehensive Multi-Section Resume Form & Validation
"""

import os
import streamlit as st
from dotenv import load_dotenv
from src.validators import validate_email, validate_url, validate_profile
from src.prompts import RESUME_SYSTEM_PROMPT, build_resume_generation_prompt
from src.claude_api import get_api_key, call_claude_json, get_mock_resume_data
from src.resume_generator import generate_resume_pipeline
from src.docx_generator import build_docx_resume
from src.ats_analyzer import analyze_ats_compatibility

# Load environment variables from .env
load_dotenv()

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="AI Resume Builder | ATS-Optimized",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# 2. CUSTOM CSS (MODERN SAAS STYLING)
# ==========================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1250px;
    }

    /* Hero Banner */
    .hero-container {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
    }

    .hero-title {
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 0.3rem;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        color: #94a3b8;
        margin-bottom: 1rem;
        font-weight: 400;
    }

    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        background-color: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }

    /* Form Card Container */
    .card-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    }

    @media (prefers-color-scheme: dark) {
        .card-box {
            background: #1e293b;
            border: 1px solid #334155;
            color: #f8fafc;
        }
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    @media (prefers-color-scheme: dark) {
        .section-title {
            color: #f8fafc;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# 3. SESSION STATE INITIALIZATION & SAMPLES
# ==========================================
def get_sample_profile():
    """Return a realistic sample candidate profile for instant testing."""
    return {
        "personal_info": {
            "full_name": "Alex Johnson",
            "professional_title": "Full Stack AI Developer",
            "email": "alex.johnson@example.com",
            "phone": "+1 (555) 234-5678",
            "location": "San Francisco, CA",
            "linkedin": "https://linkedin.com/in/alex-johnson-dev",
            "github": "https://github.com/alexjohnson-ai",
            "portfolio": "https://alexjohnson.dev",
            "summary": "Passionate software engineer with hands-on experience building full-stack web applications and integrating large language models. Strong foundation in Python, TypeScript, and modern AI APIs.",
        },
        "education": [
            {
                "institution": "University of California, Berkeley",
                "degree": "Bachelor of Science",
                "field_of_study": "Computer Science",
                "start_year": "2020",
                "end_year": "2024",
                "gpa": "3.85 / 4.0",
                "coursework": "Data Structures & Algorithms, Database Systems, Artificial Intelligence, Distributed Systems",
                "achievements": "Dean's Honor List (4 semesters), 1st Place at CalHacks 2023",
            }
        ],
        "skills": {
            "programming_languages": "Python, JavaScript, TypeScript, SQL, C++",
            "frameworks": "Streamlit, React, FastAPI, Node.js, PyTorch, Pandas",
            "databases": "PostgreSQL, MongoDB, Redis, SQLite",
            "tools": "Git, GitHub Actions, Docker, AWS (S3, EC2), VS Code, Postman",
            "soft_skills": "Problem Solving, Agile Collaboration, Cross-functional Communication, Technical Writing",
        },
        "projects": [
            {
                "name": "DocuChat - Multi-Document RAG Assistant",
                "description": "Engineered an AI conversational search engine over corporate PDF documents using retrieval-augmented generation and vector databases.",
                "technologies": "Python, FastAPI, LangChain, ChromaDB, Claude API",
                "responsibilities": "Implemented document chunking, semantic vector embeddings, and real-time streaming chat responses.",
                "results": "Decreased document search time by 65% across 200+ multi-page technical manuals.",
                "github_url": "https://github.com/alexjohnson-ai/docuchat",
                "demo_url": "https://docuchat-demo.streamlit.app",
            },
            {
                "name": "E-Commerce Real-Time Inventory Tracker",
                "description": "Architected a responsive full-stack inventory tracking dashboard with automated low-stock webhook alerts.",
                "technologies": "React, TypeScript, Node.js, PostgreSQL, Docker",
                "responsibilities": "Designed relational schema, RESTful APIs, and responsive front-end dashboard with charts.",
                "results": "Maintained sub-100ms API response latency across 50,000 product SKU queries.",
                "github_url": "https://github.com/alexjohnson-ai/inventory-tracker",
                "demo_url": "https://inventory.alexjohnson.dev",
            },
        ],
        "experience": [
            {
                "company": "NextGen AI Labs",
                "role": "AI Software Engineer Intern",
                "location": "San Francisco, CA",
                "start_date": "Jun 2023",
                "end_date": "Sep 2023",
                "responsibilities": "Collaborated with senior engineers to design and deploy LLM evaluation pipelines. Built microservices for document parsing and prompt benchmarking.",
                "achievements": "Automated prompt regression testing, cutting manual QA time by 15 hours weekly.",
                "technologies": "Python, Anthropic API, pytest, Docker, FastAPI",
            }
        ],
        "certifications": [
            {
                "name": "AWS Certified Cloud Practitioner",
                "organization": "Amazon Web Services",
                "date": "2023",
                "credential_url": "https://aws.amazon.com/verification",
            }
        ],
        "achievements": [
            "Winner of CalHacks 2023 - Best LLM Application category (out of 350+ teams)",
            "Published technical tutorial on Streamlit & LLM integrations with 15k+ reads",
        ],
        "target_job": """Senior / Junior AI Software Engineer
Job Requirements:
- Strong proficiency in Python, REST APIs, and modern web frameworks (Streamlit, FastAPI, or React)
- Hands-on experience working with LLM APIs (Anthropic Claude, OpenAI), vector search, and prompt engineering
- Solid understanding of relational databases (PostgreSQL/MySQL) and Docker containerization
- Proven ability to write clean, modular, and test-driven code (pytest)
- Excellent problem-solving, collaboration, and communication skills""",
    }


def init_session_state():
    """Ensure all required session state keys are safely initialized."""
    if "resume_data" not in st.session_state:
        st.session_state.resume_data = {
            "personal_info": {
                "full_name": "",
                "professional_title": "",
                "email": "",
                "phone": "",
                "location": "",
                "linkedin": "",
                "github": "",
                "portfolio": "",
                "summary": "",
            },
            "education": [
                {
                    "institution": "",
                    "degree": "",
                    "field_of_study": "",
                    "start_year": "",
                    "end_year": "",
                    "gpa": "",
                    "coursework": "",
                    "achievements": "",
                }
            ],
            "skills": {
                "programming_languages": "",
                "frameworks": "",
                "databases": "",
                "tools": "",
                "soft_skills": "",
            },
            "projects": [
                {
                    "name": "",
                    "description": "",
                    "technologies": "",
                    "responsibilities": "",
                    "results": "",
                    "github_url": "",
                    "demo_url": "",
                }
            ],
            "experience": [
                {
                    "company": "",
                    "role": "",
                    "location": "",
                    "start_date": "",
                    "end_date": "",
                    "responsibilities": "",
                    "achievements": "",
                    "technologies": "",
                }
            ],
            "certifications": [
                {
                    "name": "",
                    "organization": "",
                    "date": "",
                    "credential_url": "",
                }
            ],
            "achievements": [""],
            "target_job": "",
        }

    if "validation_errors" not in st.session_state:
        st.session_state.validation_errors = []

    if "validation_success" not in st.session_state:
        st.session_state.validation_success = False


init_session_state()

# ==========================================
# 4. SIDEBAR - SYSTEM STATUS & NAVIGATION
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135768.png", width=64)
    st.title("AI Resume Builder")
    st.caption("Version 1.1.0 • Phase 2")

    st.markdown("---")

    selected_page = st.radio(
        "Navigation",
        [
            "🏠 Home & Overview",
            "📝 Resume Builder",
            "📊 AI & ATS Analysis",
            "📄 Preview & Export",
        ],
        index=1,  # Default to Resume Builder during Phase 2 testing
    )

    st.markdown("---")

    # Sample Profile Helper Buttons
    st.subheader("Profile Tools")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("✨ Load Sample", help="Populates form with a realistic AI Engineer profile"):
            st.session_state.resume_data = get_sample_profile()
            st.session_state.validation_errors = []
            st.session_state.validation_success = True
            st.rerun()
    with col_btn2:
        if st.button("🧹 Clear All", help="Resets all input fields"):
            st.session_state.resume_data = {
                "personal_info": {k: "" for k in ["full_name", "professional_title", "email", "phone", "location", "linkedin", "github", "portfolio", "summary"]},
                "education": [{"institution": "", "degree": "", "field_of_study": "", "start_year": "", "end_year": "", "gpa": "", "coursework": "", "achievements": ""}],
                "skills": {k: "" for k in ["programming_languages", "frameworks", "databases", "tools", "soft_skills"]},
                "projects": [{"name": "", "description": "", "technologies": "", "responsibilities": "", "results": "", "github_url": "", "demo_url": ""}],
                "experience": [{"company": "", "role": "", "location": "", "start_date": "", "end_date": "", "responsibilities": "", "achievements": "", "technologies": ""}],
                "certifications": [{"name": "", "organization": "", "date": "", "credential_url": ""}],
                "achievements": [""],
                "target_job": "",
            }
            st.session_state.validation_errors = []
            st.session_state.validation_success = False
            st.rerun()

    st.markdown("---")
    st.subheader("Claude AI Connection")

    # Demo Mode toggle
    demo_mode = st.toggle("🧪 Demo / Mock Mode", value=False, help="Enable to test the entire application without calling the paid Claude API.")
    st.session_state.demo_mode = demo_mode

    # API key detection
    configured_key = get_api_key()
    if configured_key:
        st.success("✅ Claude API Key active")
    else:
        st.info("ℹ️ No `.env` key detected")

    with st.expander("🔑 Configure API Key", expanded=not bool(configured_key)):
        user_key = st.text_input(
            "Anthropic API Key",
            type="password",
            placeholder="sk-ant-api03-...",
            help="Your API key stays in your local browser session and is never logged or exposed.",
            value=st.session_state.get("custom_api_key", ""),
        )
        if user_key:
            st.session_state.custom_api_key = user_key
            st.success("Custom key set for this session!")
        st.caption("You can also add `ANTHROPIC_API_KEY=your_key` to a `.env` file in the project folder.")

# ==========================================
# 5. PAGE CONTENT ROUTING
# ==========================================
if selected_page == "🏠 Home & Overview":
    st.markdown(
        """
        <div class="hero-container">
            <span class="badge">🚀 Production Ready Architecture</span>
            <div class="hero-title">AI Resume Builder</div>
            <div class="hero-subtitle">
                Create an ATS-friendly resume tailored to your dream job with AI.
            </div>
            <p style="color: #cbd5e1; font-size: 0.95rem; margin: 0; max-width: 750px;">
                Built to transform your verified skills, projects, and career milestones
                into crisp, recruiter-approved bullet points — with <b>zero hallucinated qualifications</b>.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("How It Works")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("**1. Your Profile**<br>Enter your education, verified skills, projects, and experience.", unsafe_allow_html=True)
    with col2:
        st.markdown("**2. Target Job**<br>Paste your target job posting to align keywords.", unsafe_allow_html=True)
    with col3:
        st.markdown("**3. Claude AI**<br>Polishes phrasing with action verbs without inventing achievements.", unsafe_allow_html=True)
    with col4:
        st.markdown("**4. ATS Scoring**<br>Inspect ATS match score, keyword gaps, and download DOCX.", unsafe_allow_html=True)


elif selected_page == "📝 Resume Builder":
    st.title("📝 Resume Builder")
    st.caption("Fill in your details below. You can also click **'✨ Load Sample'** in the sidebar to test instantly.")

    # Validation Feedback Alerts
    if st.session_state.validation_errors:
        st.error("⚠️ Please address the following issues:")
        for err in st.session_state.validation_errors:
            st.markdown(f"- {err}")
    elif st.session_state.validation_success:
        st.success("✅ Profile data is valid and saved in session!")

    # Tabs for structured input
    tab_personal, tab_edu, tab_skills, tab_proj, tab_exp, tab_certs, tab_job = st.tabs(
        [
            "👤 Personal Info",
            "🎓 Education",
            "⚡ Skills",
            "💻 Projects",
            "💼 Experience",
            "🏆 Certs & Awards",
            "🎯 Target Job",
        ]
    )

    resume_data = st.session_state.resume_data

    # -------------------------------------------------------------
    # TAB 1: PERSONAL INFORMATION
    # -------------------------------------------------------------
    with tab_personal:
        st.subheader("Personal Information")
        p = resume_data["personal_info"]

        col1, col2 = st.columns(2)
        with col1:
            p["full_name"] = st.text_input("Full Name *", value=p.get("full_name", ""), placeholder="e.g. Alex Johnson")
            p["email"] = st.text_input("Email Address *", value=p.get("email", ""), placeholder="e.g. alex@example.com")
            if p["email"] and not validate_email(p["email"]):
                st.caption("⚠️ Invalid email format")
            p["location"] = st.text_input("Location", value=p.get("location", ""), placeholder="e.g. San Francisco, CA")
            p["linkedin"] = st.text_input("LinkedIn Profile URL", value=p.get("linkedin", ""), placeholder="https://linkedin.com/in/...")
            if p["linkedin"] and not validate_url(p["linkedin"]):
                st.caption("⚠️ Invalid URL format")

        with col2:
            p["professional_title"] = st.text_input("Target / Professional Title", value=p.get("professional_title", ""), placeholder="e.g. Software Engineer | Full Stack Developer")
            p["phone"] = st.text_input("Phone Number", value=p.get("phone", ""), placeholder="e.g. +1 (555) 019-2834")
            p["github"] = st.text_input("GitHub Profile URL", value=p.get("github", ""), placeholder="https://github.com/...")
            if p["github"] and not validate_url(p["github"]):
                st.caption("⚠️ Invalid URL format")
            p["portfolio"] = st.text_input("Portfolio / Website URL", value=p.get("portfolio", ""), placeholder="https://myportfolio.dev")
            if p["portfolio"] and not validate_url(p["portfolio"]):
                st.caption("⚠️ Invalid URL format")

        p["summary"] = st.text_area(
            "Professional Summary (Optional - Claude can optimize this for you)",
            value=p.get("summary", ""),
            height=100,
            placeholder="Brief overview of your professional background, core technical focus, and career goals.",
        )

    # -------------------------------------------------------------
    # TAB 2: EDUCATION
    # -------------------------------------------------------------
    with tab_edu:
        st.subheader("Education History")
        st.caption("Add your degree(s), institutions, and academic milestones.")

        for i, edu in enumerate(resume_data["education"]):
            with st.expander(f"🎓 Education #{i+1}: {edu.get('degree', '')} {edu.get('institution', '') or 'New Entry'}", expanded=True):
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    edu["institution"] = st.text_input(f"Institution / University #{i+1}", value=edu.get("institution", ""), key=f"edu_inst_{i}", placeholder="e.g. UC Berkeley")
                    edu["degree"] = st.text_input(f"Degree #{i+1}", value=edu.get("degree", ""), key=f"edu_deg_{i}", placeholder="e.g. Bachelor of Science")
                    edu["field_of_study"] = st.text_input(f"Field of Study #{i+1}", value=edu.get("field_of_study", ""), key=f"edu_field_{i}", placeholder="e.g. Computer Science")
                with col_e2:
                    edu["gpa"] = st.text_input(f"CGPA / GPA #{i+1}", value=edu.get("gpa", ""), key=f"edu_gpa_{i}", placeholder="e.g. 3.8 / 4.0")
                    col_y1, col_y2 = st.columns(2)
                    with col_y1:
                        edu["start_year"] = st.text_input(f"Start Year #{i+1}", value=edu.get("start_year", ""), key=f"edu_start_{i}", placeholder="2020")
                    with col_y2:
                        edu["end_year"] = st.text_input(f"Graduation Year #{i+1}", value=edu.get("end_year", ""), key=f"edu_end_{i}", placeholder="2024")

                edu["coursework"] = st.text_input(
                    f"Relevant Coursework #{i+1}",
                    value=edu.get("coursework", ""),
                    key=f"edu_course_{i}",
                    placeholder="e.g. Data Structures, Algorithms, Distributed Systems, Machine Learning",
                )
                edu["achievements"] = st.text_input(
                    f"Academic Honors / Awards #{i+1}",
                    value=edu.get("achievements", ""),
                    key=f"edu_honors_{i}",
                    placeholder="e.g. Dean's Honors List, Magna Cum Laude",
                )

                if len(resume_data["education"]) > 1:
                    if st.button(f"🗑️ Remove Education #{i+1}", key=f"del_edu_{i}"):
                        resume_data["education"].pop(i)
                        st.rerun()

        if st.button("➕ Add Another Education", key="add_edu_btn"):
            resume_data["education"].append(
                {
                    "institution": "",
                    "degree": "",
                    "field_of_study": "",
                    "start_year": "",
                    "end_year": "",
                    "gpa": "",
                    "coursework": "",
                    "achievements": "",
                }
            )
            st.rerun()

    # -------------------------------------------------------------
    # TAB 3: SKILLS
    # -------------------------------------------------------------
    with tab_skills:
        st.subheader("Technical & Soft Skills")
        st.caption("Provide comma-separated skills that you genuinely possess. The AI will never invent skills.")

        s = resume_data["skills"]
        s["programming_languages"] = st.text_input(
            "Programming Languages",
            value=s.get("programming_languages", ""),
            placeholder="e.g. Python, Java, TypeScript, C++, SQL",
        )
        s["frameworks"] = st.text_input(
            "Frameworks & Libraries",
            value=s.get("frameworks", ""),
            placeholder="e.g. Streamlit, React, FastAPI, Node.js, PyTorch, Pandas",
        )
        s["databases"] = st.text_input(
            "Databases & Storage",
            value=s.get("databases", ""),
            placeholder="e.g. PostgreSQL, MongoDB, Redis, MySQL",
        )
        s["tools"] = st.text_input(
            "Developer Tools & Cloud",
            value=s.get("tools", ""),
            placeholder="e.g. Git, GitHub Actions, Docker, AWS, VS Code, Postman",
        )
        s["soft_skills"] = st.text_input(
            "Core Strengths & Soft Skills",
            value=s.get("soft_skills", ""),
            placeholder="e.g. Problem Solving, Cross-functional Collaboration, Agile Methodology",
        )

    # -------------------------------------------------------------
    # TAB 4: PROJECTS
    # -------------------------------------------------------------
    with tab_proj:
        st.subheader("Technical Projects")
        st.caption("Describe your projects naturally. Claude will turn your descriptions into high-impact bullet points.")

        for j, proj in enumerate(resume_data["projects"]):
            with st.expander(f"💻 Project #{j+1}: {proj.get('name', '') or 'New Project'}", expanded=True):
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    proj["name"] = st.text_input(f"Project Name #{j+1}", value=proj.get("name", ""), key=f"proj_name_{j}", placeholder="e.g. AI Resume Builder")
                    proj["technologies"] = st.text_input(f"Technologies Used #{j+1}", value=proj.get("technologies", ""), key=f"proj_tech_{j}", placeholder="e.g. Python, Streamlit, Claude API")
                with col_p2:
                    proj["github_url"] = st.text_input(f"GitHub Repository URL #{j+1}", value=proj.get("github_url", ""), key=f"proj_gh_{j}", placeholder="https://github.com/...")
                    proj["demo_url"] = st.text_input(f"Live Demo URL #{j+1}", value=proj.get("demo_url", ""), key=f"proj_demo_{j}", placeholder="https://...")

                proj["description"] = st.text_area(
                    f"What does this project do? #{j+1}",
                    value=proj.get("description", ""),
                    key=f"proj_desc_{j}",
                    height=80,
                    placeholder="e.g. Built an interactive web app that helps job seekers tailor their resumes to ATS requirements.",
                )
                proj["responsibilities"] = st.text_input(
                    f"What were your specific contributions? #{j+1}",
                    value=proj.get("responsibilities", ""),
                    key=f"proj_resp_{j}",
                    placeholder="e.g. Designed the state management, created modular DOCX export, and integrated Claude API.",
                )
                proj["results"] = st.text_input(
                    f"Measurable Results / Impact (Only if real) #{j+1}",
                    value=proj.get("results", ""),
                    key=f"proj_res_{j}",
                    placeholder="e.g. Used by 100+ classmates; reduced resume formatting time by 80%.",
                )

                if len(resume_data["projects"]) > 1:
                    if st.button(f"🗑️ Remove Project #{j+1}", key=f"del_proj_{j}"):
                        resume_data["projects"].pop(j)
                        st.rerun()

        if st.button("➕ Add Another Project", key="add_proj_btn"):
            resume_data["projects"].append(
                {
                    "name": "",
                    "description": "",
                    "technologies": "",
                    "responsibilities": "",
                    "results": "",
                    "github_url": "",
                    "demo_url": "",
                }
            )
            st.rerun()

    # -------------------------------------------------------------
    # TAB 5: EXPERIENCE & INTERNSHIPS
    # -------------------------------------------------------------
    with tab_exp:
        st.subheader("Work & Internship Experience")
        st.caption("Include relevant internships, part-time, or full-time roles.")

        for k, exp in enumerate(resume_data["experience"]):
            with st.expander(f"💼 Experience #{k+1}: {exp.get('role', '')} at {exp.get('company', '') or 'New Role'}", expanded=True):
                col_x1, col_x2 = st.columns(2)
                with col_x1:
                    exp["company"] = st.text_input(f"Company / Organization #{k+1}", value=exp.get("company", ""), key=f"exp_comp_{k}", placeholder="e.g. TechCorp")
                    exp["role"] = st.text_input(f"Job Role / Title #{k+1}", value=exp.get("role", ""), key=f"exp_role_{k}", placeholder="e.g. Software Engineer Intern")
                    exp["location"] = st.text_input(f"Location #{k+1}", value=exp.get("location", ""), key=f"exp_loc_{k}", placeholder="e.g. Remote / New York, NY")
                with col_x2:
                    col_d1, col_d2 = st.columns(2)
                    with col_d1:
                        exp["start_date"] = st.text_input(f"Start Date #{k+1}", value=exp.get("start_date", ""), key=f"exp_sd_{k}", placeholder="e.g. Jun 2023")
                    with col_d2:
                        exp["end_date"] = st.text_input(f"End Date #{k+1}", value=exp.get("end_date", ""), key=f"exp_ed_{k}", placeholder="e.g. Present / Sep 2023")
                    exp["technologies"] = st.text_input(f"Technologies Used #{k+1}", value=exp.get("technologies", ""), key=f"exp_tech_{k}", placeholder="e.g. Python, SQL, Git, AWS")

                exp["responsibilities"] = st.text_area(
                    f"Responsibilities & Day-to-day work #{k+1}",
                    value=exp.get("responsibilities", ""),
                    key=f"exp_resp_{k}",
                    height=80,
                    placeholder="e.g. Developed REST APIs for internal analytics dashboard. Collaborated in daily standups.",
                )
                exp["achievements"] = st.text_input(
                    f"Key Achievements #{k+1}",
                    value=exp.get("achievements", ""),
                    key=f"exp_ach_{k}",
                    placeholder="e.g. Optimized database queries to reduce endpoint response time by 30%.",
                )

                if len(resume_data["experience"]) > 1:
                    if st.button(f"🗑️ Remove Experience #{k+1}", key=f"del_exp_{k}"):
                        resume_data["experience"].pop(k)
                        st.rerun()

        if st.button("➕ Add Another Experience", key="add_exp_btn"):
            resume_data["experience"].append(
                {
                    "company": "",
                    "role": "",
                    "location": "",
                    "start_date": "",
                    "end_date": "",
                    "responsibilities": "",
                    "achievements": "",
                    "technologies": "",
                }
            )
            st.rerun()

    # -------------------------------------------------------------
    # TAB 6: CERTIFICATIONS & ACHIEVEMENTS
    # -------------------------------------------------------------
    with tab_certs:
        st.subheader("Certifications")
        for m, cert in enumerate(resume_data["certifications"]):
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                cert["name"] = st.text_input(f"Certification Name #{m+1}", value=cert.get("name", ""), key=f"cert_nm_{m}", placeholder="e.g. AWS Certified Developer")
                cert["organization"] = st.text_input(f"Issuing Organization #{m+1}", value=cert.get("organization", ""), key=f"cert_org_{m}", placeholder="e.g. Amazon Web Services")
            with col_c2:
                cert["date"] = st.text_input(f"Issue Year / Date #{m+1}", value=cert.get("date", ""), key=f"cert_dt_{m}", placeholder="e.g. 2023")
                cert["credential_url"] = st.text_input(f"Credential URL #{m+1}", value=cert.get("credential_url", ""), key=f"cert_url_{m}", placeholder="https://...")

        if st.button("➕ Add Certification", key="add_cert_btn"):
            resume_data["certifications"].append({"name": "", "organization": "", "date": "", "credential_url": ""})
            st.rerun()

        st.markdown("---")
        st.subheader("Honors, Awards & Achievements")
        st.caption("Hackathons, competitions, awards, leadership, or open-source contributions.")

        for n, ach in enumerate(resume_data["achievements"]):
            resume_data["achievements"][n] = st.text_input(
                f"Achievement #{n+1}",
                value=ach,
                key=f"ach_item_{n}",
                placeholder="e.g. 1st Place at National Hackathon (out of 200 teams)",
            )

        if st.button("➕ Add Achievement", key="add_ach_btn"):
            resume_data["achievements"].append("")
            st.rerun()

    # -------------------------------------------------------------
    # TAB 7: TARGET JOB DESCRIPTION
    # -------------------------------------------------------------
    with tab_job:
        st.subheader("Target Job Description")
        st.caption("Paste the full job posting here. Claude will use this to align your keywords, detect missing skills, and calculate ATS compatibility.")

        resume_data["target_job"] = st.text_area(
            "Job Description (Optional but recommended)",
            value=resume_data.get("target_job", ""),
            height=220,
            placeholder="Paste responsibilities, required qualifications, and desired technical skills from the job description...",
        )

    # -------------------------------------------------------------
    # SAVE & VALIDATE PROFILE BUTTON
    # -------------------------------------------------------------
    st.markdown("---")
    col_save, col_gen, col_info = st.columns([1, 1.2, 1.5])

    # Helper function to prepare payload
    def prepare_payload():
        packaged_data = dict(resume_data)
        packaged_skills = {}
        for category, raw_str in resume_data["skills"].items():
            if isinstance(raw_str, str):
                packaged_skills[category] = [s.strip() for s in raw_str.split(",") if s.strip()]
            else:
                packaged_skills[category] = raw_str
        packaged_data["skills"] = packaged_skills
        return packaged_data

    with col_save:
        if st.button("💾 Save Profile", use_container_width=True):
            packaged_data = prepare_payload()
            is_valid, errors = validate_profile(packaged_data)
            st.session_state.validation_errors = errors
            st.session_state.validation_success = is_valid

            if is_valid:
                st.session_state.resume_data = resume_data
                st.toast("Profile data validated and saved!", icon="✅")
            st.rerun()

    with col_gen:
        if st.button("🚀 Generate Resume with AI", type="primary", use_container_width=True):
            packaged_data = prepare_payload()
            is_valid, errors = validate_profile(packaged_data)
            st.session_state.validation_errors = errors
            st.session_state.validation_success = is_valid

            if not is_valid:
                st.rerun()

            # Execute Generation using the unified pipeline
            with st.spinner("🤖 Claude AI is crafting your ATS-optimized resume..."):
                active_key = st.session_state.get("custom_api_key") or get_api_key()
                demo_mode = st.session_state.get("demo_mode", False)

                success, result, msg = generate_resume_pipeline(
                    raw_profile=packaged_data,
                    target_job=packaged_data.get("target_job", ""),
                    custom_api_key=active_key,
                    demo_mode=demo_mode,
                )

                if success and result:
                    st.session_state.generated_resume = result

                    # Automatically run ATS analysis against target job
                    _, ats_res, _ = analyze_ats_compatibility(
                        resume_data=result,
                        target_job=packaged_data.get("target_job", ""),
                        custom_api_key=active_key,
                        demo_mode=demo_mode,
                    )
                    st.session_state.ats_analysis = ats_res

                    st.toast("Resume & ATS Analysis generated successfully!", icon="✅")
                    st.success(f"✨ {msg} Navigate to **'📊 AI & ATS Analysis'** or **'📄 Preview & Export'**!")
                else:
                    st.error(msg)

    with col_info:
        st.caption("AI rewrites project & experience bullets into impact-driven ATS statements without fabricating qualifications.")


elif selected_page == "📊 AI & ATS Analysis":
    st.header("📊 AI & ATS Compatibility Analysis")
    st.caption("Evaluate your resume against target job requirements and identify keyword gaps.")

    # Re-run or trigger analysis button
    packaged_profile = dict(st.session_state.resume_data)
    target_job_text = packaged_profile.get("target_job", "")

    col_btn, col_txt = st.columns([1, 2.5])
    with col_btn:
        if st.button("🔄 Run / Refresh ATS Analysis", type="primary", use_container_width=True):
            with st.spinner("Analyzing profile against target job description..."):
                active_key = st.session_state.get("custom_api_key") or get_api_key()
                demo_mode = st.session_state.get("demo_mode", False)
                source_data = st.session_state.get("generated_resume") or packaged_profile

                success, ats_res, msg = analyze_ats_compatibility(
                    resume_data=source_data,
                    target_job=target_job_text,
                    custom_api_key=active_key,
                    demo_mode=demo_mode,
                )
                if success and ats_res:
                    st.session_state.ats_analysis = ats_res
                    st.toast("ATS analysis updated!", icon="🎯")
                st.rerun()

    with col_txt:
        if target_job_text.strip():
            st.caption(f"🎯 Target Job Description detected ({len(target_job_text.split())} words).")
        else:
            st.caption("ℹ️ No target job description provided. Analysis is evaluating general ATS industry standards.")

    ats_data = st.session_state.get("ats_analysis")

    if not ats_data:
        st.info("👋 Click **'🔄 Run / Refresh ATS Analysis'** above or generate your resume to see your comprehensive ATS score and keyword gap analysis.")
    else:
        score = ats_data.get("overall_score", 75)

        # 1. OVERALL SCORE CARD
        st.markdown("---")
        col_score, col_verdict = st.columns([1, 2])

        with col_score:
            if score >= 80:
                badge_color = "#10b981"  # Emerald Green
                badge_text = "✨ High Compatibility (80-100)"
            elif score >= 60:
                badge_color = "#f59e0b"  # Amber
                badge_text = "⚠️ Moderate Match (60-79)"
            else:
                badge_color = "#ef4444"  # Red
                badge_text = "🚨 Low Match (<60)"

            st.metric("Estimated ATS Score", f"{score} / 100")
            st.markdown(
                f"""
                <div style='background-color: {badge_color}20; color: {badge_color};
                            border: 1px solid {badge_color}50; padding: 6px 12px;
                            border-radius: 9999px; display: inline-block; font-weight: 600; font-size: 0.85rem;'>
                    {badge_text}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_verdict:
            st.markdown("### Recruiter Assessment")
            st.write(ats_data.get("summary_verdict", "Strong candidate profile."))
            st.caption("*Note: This is an estimated compatibility score based on keyword overlap, structural completeness, and skill relevance. It is not an official score from a specific ATS vendor.*")

        # 2. SCORE BREAKDOWN
        st.markdown("---")
        st.subheader("Score Breakdown")
        breakdown = ats_data.get("score_breakdown", {})

        cols = st.columns(len(breakdown) if breakdown else 1)
        for idx, (cat_key, cat_data) in enumerate(breakdown.items()):
            with cols[idx]:
                c_score = cat_data.get("score", 0)
                c_max = cat_data.get("max_score", 20)
                label = cat_data.get("label", cat_key.title())
                ratio = c_score / c_max if c_max else 0
                st.metric(label, f"{c_score} / {c_max}")
                st.progress(ratio)

        # 3. KEYWORD ANALYSIS (MATCHED VS MISSING)
        st.markdown("---")
        st.subheader("Keyword & Skills Alignment")

        col_matched, col_missing = st.columns(2)

        with col_matched:
            st.markdown("#### ✅ Matched Keywords & Skills")
            matched = ats_data.get("matched_keywords", [])
            if matched:
                chips_html = " ".join([
                    f"<span style='display: inline-block; background-color: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); padding: 4px 10px; border-radius: 6px; margin: 3px; font-weight: 500; font-size: 0.85rem;'>✓ {kw}</span>"
                    for kw in matched
                ])
                st.markdown(chips_html, unsafe_allow_html=True)
            else:
                st.caption("No specific technical keywords matched yet.")

        with col_missing:
            st.markdown("#### ⚠️ Missing Keywords (Requested in Job)")
            missing = ats_data.get("missing_keywords", [])
            if missing:
                chips_html = " ".join([
                    f"<span style='display: inline-block; background-color: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); padding: 4px 10px; border-radius: 6px; margin: 3px; font-weight: 500; font-size: 0.85rem;'>+ {kw}</span>"
                    for kw in missing
                ])
                st.markdown(chips_html, unsafe_allow_html=True)
                st.markdown(
                    """
                    <div style='font-size: 0.82rem; color: #64748b; margin-top: 8px;'>
                    💡 <b>Important:</b> If a skill is missing from your profile, <b>do NOT invent it</b>. Consider adding it only if you genuinely have hands-on experience with it.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.success("No critical keywords missing from the job description!")

        # 4. ACTIONABLE IMPROVEMENT SUGGESTIONS
        st.markdown("---")
        st.subheader("Actionable Improvement Suggestions")
        suggestions = ats_data.get("improvement_suggestions", [])
        for sug in suggestions:
            st.markdown(f"- 💡 {sug}")


elif selected_page == "📄 Preview & Export":
    st.header("📄 Resume Preview & Export")
    st.caption("Review your generated resume in multiple ATS-tailored formats.")

    gen_resume = st.session_state.get("generated_resume")
    if not gen_resume:
        st.warning("⚠️ No resume has been generated yet.")
        st.info("Go to **'📝 Resume Builder'** and click **'🚀 Generate Resume with AI'** to create your ATS resume.")
    else:
        # Prepare download payloads
        full_name_clean = gen_resume.get("personal_info", {}).get("full_name", "Resume").replace(" ", "_")
        docx_buffer = build_docx_resume(gen_resume)
        docx_bytes = docx_buffer.getvalue()

        # Actions bar with all ATS download options
        col_view1, col_view2, col_view3 = st.columns([1.5, 1.2, 1])
        with col_view1:
            st.download_button(
                "📥 Download ATS DOCX (.docx)",
                data=docx_bytes,
                file_name=f"{full_name_clean}_Resume.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
                use_container_width=True,
                help="Recommended: Fully editable Microsoft Word document with perfect ATS formatting.",
            )
        with col_view2:
            st.download_button(
                "🌐 Download HTML (Print to PDF)",
                data=gen_resume.get("_rendered_html", ""),
                file_name=f"{full_name_clean}_Resume.html",
                mime="text/html",
                use_container_width=True,
                help="Opens in any browser. Press Ctrl + P to save as vector PDF.",
            )
        with col_view3:
            st.download_button(
                "📄 Download Plain Text (.txt)",
                data=gen_resume.get("_rendered_text", ""),
                file_name=f"{full_name_clean}_Resume.txt",
                mime="text/plain",
                use_container_width=True,
                help="Unformatted plain text for direct ATS portal copy-pasting.",
            )

        # Multi-tab preview
        prev_tab_doc, prev_tab_text, prev_tab_md, prev_tab_json = st.tabs(
            [
                "📑 ATS Document View",
                "📋 Plain Text (Copy-Paste)",
                "📝 Markdown View",
                "⚙️ Structured JSON",
            ]
        )

        with prev_tab_doc:
            st.caption("💡 **Tip:** This layout strictly obeys standard ATS single-column formatting. You can print directly or save as PDF using your browser (Ctrl + P).")
            # Render HTML inside an iframe component
            html_content = gen_resume.get("_rendered_html", "")
            st.components.v1.html(html_content, height=850, scrolling=True)

        with prev_tab_text:
            st.caption("Copy this plain-text representation directly into job application portals (Workday, Taleo, Greenhouse):")
            st.text_area(
                "ATS Plain Text Content",
                value=gen_resume.get("_rendered_text", ""),
                height=500,
                help="Click inside and press Ctrl + A, Ctrl + C to copy.",
            )

        with prev_tab_md:
            st.caption("Clean GitHub-flavored markdown:")
            st.markdown(gen_resume.get("_rendered_markdown", ""))

        with prev_tab_json:
            st.caption("Raw structured data received from Claude AI:")
            st.json(gen_resume)

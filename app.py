"""
Main Streamlit Application for AI Resume Builder.
A modern, production-grade, 100% local, ATS-friendly resume generator and analyzer.
"""
import os
import sys
from pathlib import Path
import streamlit as st

# Ensure project root is in python path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import config
from models.resume_schema import (
    ResumeData,
    PersonalInfo,
    EducationEntry,
    SkillsData,
    SkillCategory,
    ExperienceEntry,
    ProjectEntry,
    CertificationEntry,
    AchievementEntry,
    VolunteerEntry,
    TargetJob,
)
from ai.ollama_client import OllamaClient
from ai.resume_generator import (
    generate_professional_summary,
    improve_experience_bullets,
    improve_project_bullets,
)
from ai.analyzer import (
    calculate_ats_score,
    match_resume_with_job,
    analyze_resume_with_ai,
)
from resume.templates import RESUME_TEMPLATES, TEMPLATE_CONFIGS
from resume.renderer import render_resume_html
from resume.pdf_generator import generate_resume_pdf
from resume.docx_generator import generate_resume_docx
from utils.validation import validate_email, validate_url, validate_phone
from utils.helpers import generate_resume_filename, split_lines_or_commas
from utils.sample_data import get_sample_resume_data


# --- Page Configuration ---
st.set_page_config(
    page_title=f"{config.APP_TITLE} — ATS Resume Generator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load CSS
css_file = BASE_DIR / "assets" / "custom.css"
if css_file.exists():
    with open(css_file, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# --- Session State Initialization ---
if "resume_data" not in st.session_state:
    st.session_state.resume_data = ResumeData()

groq_key = ""
try:
    groq_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
except Exception:
    groq_key = os.getenv("GROQ_API_KEY", "")

if groq_key:
    ai_client = GroqClient(api_key=groq_key)
else:
    ollama_url = config.OLLAMA_BASE_URL
    try:
        ollama_url = st.secrets.get("OLLAMA_BASE_URL", config.OLLAMA_BASE_URL)
    except Exception:
        pass
    ai_client = OllamaClient(
        base_url=ollama_url,
        model=config.OLLAMA_MODEL,
    )


# --- Helper to load sample data ---
def load_sample():
    st.session_state.resume_data = get_sample_resume_data()
    st.toast("✅ Sample demo profile loaded successfully!", icon="📋")


def clear_form():
    st.session_state.resume_data = ResumeData()
    st.toast("🧹 Form cleared. Ready for fresh resume entry.", icon="✨")


# --- Sidebar Navigation & Controls ---
with st.sidebar:
    st.title("📄 AI Resume Builder")
    st.caption("ATS-Friendly • Professional • Dual Export")

    # Privacy statement badge
    st.markdown(
        f"<div class='privacy-badge'>{config.PRIVACY_STATEMENT}</div>",
        unsafe_allow_html=True,
    )

    # AI Status Pill
    is_online, _ = ai_client.is_available()
    if is_online:
        st.markdown(
            f"<div class='status-pill status-online'>● AI Assistant Ready</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div class='status-pill status-offline'>● AI Assistant Offline</div>",
            unsafe_allow_html=True,
        )

    st.divider()

    # Template Selector
    st.subheader("🎨 Resume Template")
    selected_tpl = st.selectbox(
        "Choose Design",
        options=RESUME_TEMPLATES,
        index=RESUME_TEMPLATES.index(st.session_state.resume_data.selected_template)
        if st.session_state.resume_data.selected_template in RESUME_TEMPLATES else 0,
    )
    if selected_tpl != st.session_state.resume_data.selected_template:
        st.session_state.resume_data.selected_template = selected_tpl

    # Template description
    tpl_desc = TEMPLATE_CONFIGS[st.session_state.resume_data.selected_template]["description"]
    st.caption(f"ℹ️ {tpl_desc}")

    st.divider()

    # Section Visibility Selector
    st.subheader("📑 Visible Sections")
    active_sections = st.multiselect(
        "Toggle Sections",
        options=config.AVAILABLE_SECTIONS,
        default=st.session_state.resume_data.enabled_sections,
    )
    st.session_state.resume_data.enabled_sections = active_sections

    st.divider()

    # Quick Action Buttons
    col_demo, col_reset = st.columns(2)
    with col_demo:
        if st.button("📋 Load Demo", use_container_width=True, help="Load a pre-filled student resume to test instantly"):
            load_sample()
            st.rerun()
    with col_reset:
        if st.button("🧹 Clear Form", use_container_width=True, help="Reset all fields"):
            clear_form()
            st.rerun()

    st.markdown("---")
    st.caption("Version 1.0.0 • Local AI Engine")


# --- Main Content Header ---
st.title(config.APP_TITLE)
st.markdown(f"**{config.APP_SUBTITLE}**")

# Notice if AI features are offline
if not is_online:
    st.info(
        "💡 **Notice:** Automated AI assistant is currently in manual mode on this public instance. "
        "All resume editing, live preview, 3 ATS templates, ATS scoring, Job Matcher, PDF download, and Word DOCX download are 100% active!"
    )


# --- Tabs Organization ---
tabs = st.tabs([
    "👤 Contact",
    "📝 Summary",
    "🎓 Education",
    "⚡ Skills",
    "💼 Experience",
    "🚀 Projects",
    "📜 Certs & Honors",
    "🎯 Job Match & ATS",
    "👁️ Live Preview & Export",
])

res = st.session_state.resume_data


# ==========================================
# TAB 1: Contact / Personal Information
# ==========================================
with tabs[0]:
    st.subheader("Personal & Contact Details")
    st.caption("Recruiters and ATS systems require standard contact channels.")

    col1, col2 = st.columns(2)
    with col1:
        res.personal_info.full_name = st.text_input(
            "Full Name *",
            value=res.personal_info.full_name,
            placeholder="e.g. Alex Chen",
        )
        res.personal_info.email = st.text_input(
            "Professional Email *",
            value=res.personal_info.email,
            placeholder="alex.chen@example.com",
        )
        if res.personal_info.email:
            valid, msg = validate_email(res.personal_info.email)
            if not valid:
                st.caption(f":red[⚠️ {msg}]")

        res.personal_info.phone = st.text_input(
            "Phone Number *",
            value=res.personal_info.phone,
            placeholder="+1 (555) 019-2834",
        )
        if res.personal_info.phone:
            valid, msg = validate_phone(res.personal_info.phone)
            if not valid:
                st.caption(f":orange[⚠️ {msg}]")

    with col2:
        res.personal_info.location = st.text_input(
            "Location (City, State / Country)",
            value=res.personal_info.location,
            placeholder="San Jose, CA",
        )
        res.personal_info.linkedin_url = st.text_input(
            "LinkedIn Profile URL",
            value=res.personal_info.linkedin_url,
            placeholder="https://linkedin.com/in/alexchen",
        )
        if res.personal_info.linkedin_url:
            valid, val = validate_url(res.personal_info.linkedin_url)
            if not valid:
                st.caption(f":orange[⚠️ {val}]")
            else:
                res.personal_info.linkedin_url = val

        res.personal_info.github_url = st.text_input(
            "GitHub Profile URL",
            value=res.personal_info.github_url,
            placeholder="https://github.com/alexchen",
        )
        if res.personal_info.github_url:
            valid, val = validate_url(res.personal_info.github_url)
            if not valid:
                st.caption(f":orange[⚠️ {val}]")
            else:
                res.personal_info.github_url = val

        res.personal_info.portfolio_url = st.text_input(
            "Portfolio / Personal Website URL",
            value=res.personal_info.portfolio_url,
            placeholder="https://alexchen.dev",
        )
        if res.personal_info.portfolio_url:
            valid, val = validate_url(res.personal_info.portfolio_url)
            if not valid:
                st.caption(f":orange[⚠️ {val}]")
            else:
                res.personal_info.portfolio_url = val


# ==========================================
# TAB 2: Professional Summary
# ==========================================
with tabs[1]:
    st.subheader("Professional Summary")
    st.caption("A punchy 2-4 sentence introduction highlighting your academic core and engineering capabilities.")

    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        if st.button("✨ Generate with AI", disabled=not is_online, help="Generate a truthful summary using AI"):
            with st.spinner("AI is synthesizing your career details..."):
                try:
                    generated_summary = generate_professional_summary(res, ai_client)
                    res.summary = generated_summary
                    st.success("Summary generated!")
                except Exception as e:
                    st.error(f"Generation error: {str(e)}")

    with col_info:
        if not is_online:
            st.caption("AI generation is offline on this public instance. You can write or edit your summary directly below.")
        else:
            st.caption("The AI strictly synthesizes your education, skills, and projects without inventing fake metrics.")

    res.summary = st.text_area(
        "Edit or write your professional summary directly:",
        value=res.summary,
        height=140,
        placeholder="e.g. Motivated Computer Science undergraduate with hands-on experience in Python automation and full-stack web development...",
    )


# ==========================================
# TAB 3: Education
# ==========================================
with tabs[2]:
    st.subheader("Education History")
    st.caption("List university, degree, graduation timelines, GPA, and coursework.")

    if not res.education:
        res.education.append(EducationEntry())

    to_remove_edu = None
    for idx, edu in enumerate(res.education):
        with st.expander(f"🎓 Education #{idx + 1}: {edu.institution or 'New Entry'}", expanded=True):
            ec1, ec2 = st.columns(2)
            with ec1:
                edu.institution = st.text_input("Institution / University", value=edu.institution, key=f"edu_inst_{idx}")
                edu.degree = st.text_input("Degree (e.g. B.S., B.Tech, M.S.)", value=edu.degree, key=f"edu_deg_{idx}")
                edu.field_of_study = st.text_input("Field of Study / Major", value=edu.field_of_study, key=f"edu_field_{idx}")
            with ec2:
                ed_c1, ed_c2 = st.columns(2)
                with ed_c1:
                    edu.start_year = st.text_input("Start Year", value=edu.start_year, key=f"edu_start_{idx}")
                with ed_c2:
                    edu.end_year = st.text_input("Graduation Year", value=edu.end_year, key=f"edu_end_{idx}")
                edu.gpa = st.text_input("GPA / Score (Optional)", value=edu.gpa, key=f"edu_gpa_{idx}")
                edu.relevant_coursework = st.text_input(
                    "Relevant Coursework (Optional, comma-separated)",
                    value=edu.relevant_coursework,
                    key=f"edu_cw_{idx}",
                )

            if len(res.education) > 1:
                if st.button("🗑️ Remove this education entry", key=f"del_edu_{idx}"):
                    to_remove_edu = idx

    if to_remove_edu is not None:
        res.education.pop(to_remove_edu)
        st.rerun()

    if st.button("➕ Add Another Education Entry"):
        res.education.append(EducationEntry())
        st.rerun()


# ==========================================
# TAB 4: Skills
# ==========================================
with tabs[3]:
    st.subheader("Categorized Technical Skills")
    st.caption("Enter comma-separated items for each category. ATS parsers categorize skills into standardized taxonomies.")

    sk = res.skills
    c_lang, c_frame = st.columns(2)
    with c_lang:
        raw_lang = st.text_input(
            "Programming Languages",
            value=", ".join(sk.programming_languages),
            placeholder="Python, Java, C++, JavaScript, SQL",
            help="Comma-separated list",
        )
        sk.programming_languages = split_lines_or_commas(raw_lang)

        raw_tools = st.text_input(
            "Developer Tools & Platforms",
            value=", ".join(sk.tools),
            placeholder="Git, GitHub, Docker, VS Code, Postman, Linux",
        )
        sk.tools = split_lines_or_commas(raw_tools)

        raw_db = st.text_input(
            "Databases",
            value=", ".join(sk.databases),
            placeholder="PostgreSQL, MySQL, MongoDB, Redis, SQLite",
        )
        sk.databases = split_lines_or_commas(raw_db)

    with c_frame:
        raw_frame = st.text_input(
            "Frameworks & Libraries",
            value=", ".join(sk.frameworks),
            placeholder="Streamlit, Flask, FastAPI, React, Node.js",
        )
        sk.frameworks = split_lines_or_commas(raw_frame)

        raw_ai = st.text_input(
            "AI / Machine Learning",
            value=", ".join(sk.ai_ml),
            placeholder="PyTorch, Scikit-learn, LangChain, Ollama, Pandas, NumPy",
        )
        sk.ai_ml = split_lines_or_commas(raw_ai)

    # Custom categories
    st.write("**Custom Categories (Optional)**")
    to_remove_cat = None
    for c_idx, cat in enumerate(sk.custom_categories):
        cc1, cc2, cc3 = st.columns([2, 4, 1])
        with cc1:
            cat.category_name = st.text_input("Category Name", value=cat.category_name, key=f"cat_name_{c_idx}")
        with cc2:
            raw_c_skills = st.text_input("Skills (comma-separated)", value=", ".join(cat.skills), key=f"cat_skills_{c_idx}")
            cat.skills = split_lines_or_commas(raw_c_skills)
        with cc3:
            st.write("")
            st.write("")
            if st.button("🗑️", key=f"del_cat_{c_idx}"):
                to_remove_cat = c_idx

    if to_remove_cat is not None:
        sk.custom_categories.pop(to_remove_cat)
        st.rerun()

    if st.button("➕ Add Custom Skill Category"):
        sk.custom_categories.append(SkillCategory(category_name="Cloud & DevOps", skills=[]))
        st.rerun()


# ==========================================
# TAB 5: Experience
# ==========================================
with tabs[4]:
    st.subheader("Professional Experience & Internships")
    st.caption("Include roles, companies, key responsibilities, and use AI to enhance phrasing into impact-focused action verbs.")

    if not res.experience:
        res.experience.append(ExperienceEntry())

    to_remove_exp = None
    for idx, exp in enumerate(res.experience):
        header_title = f"{exp.role or 'Role'} at {exp.company or 'Company'}"
        with st.expander(f"💼 Experience #{idx + 1}: {header_title}", expanded=True):
            xc1, xc2 = st.columns(2)
            with xc1:
                exp.company = st.text_input("Company / Organization", value=exp.company, key=f"exp_comp_{idx}")
                exp.role = st.text_input("Job Title / Role", value=exp.role, key=f"exp_role_{idx}")
                exp.location = st.text_input("Location (City, State / Remote)", value=exp.location, key=f"exp_loc_{idx}")
            with xc2:
                xd1, xd2 = st.columns(2)
                with xd1:
                    exp.start_date = st.text_input("Start Date", value=exp.start_date, key=f"exp_start_{idx}", placeholder="Jun 2024")
                with xd2:
                    if not exp.is_current:
                        exp.end_date = st.text_input("End Date", value=exp.end_date, key=f"exp_end_{idx}", placeholder="Aug 2024")
                    else:
                        st.text_input("End Date", value="Present", disabled=True, key=f"exp_end_dis_{idx}")
                exp.is_current = st.checkbox("Currently working here", value=exp.is_current, key=f"exp_curr_{idx}")

            exp.responsibilities = st.text_area(
                "Responsibilities & Tasks (What did you do?)",
                value=exp.responsibilities,
                key=f"exp_resp_{idx}",
                placeholder="e.g. Developed REST APIs using FastAPI. Wrote unit tests. Handled database migrations.",
                height=90,
            )
            exp.achievements = st.text_area(
                "Measurable Results & Outcomes (Optional - do not invent numbers)",
                value=exp.achievements,
                key=f"exp_ach_{idx}",
                placeholder="e.g. Reduced API latency by optimizing queries. Achieved 90% test coverage.",
                height=70,
            )

            # AI Improvement Action
            btn_col, stat_col = st.columns([1, 3])
            with btn_col:
                if st.button(f"⚡ Improve with AI", key=f"btn_ai_exp_{idx}", disabled=not is_online):
                    if not exp.responsibilities.strip():
                        st.warning("Please enter your responsibilities first before improving.")
                    else:
                        with st.spinner("Refining bullet points with strong action verbs..."):
                            try:
                                bullets = improve_experience_bullets(exp, res.target_job, ai_client)
                                exp.improved_bullets = bullets
                                st.success("Bullets updated!")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")

            with stat_col:
                if exp.improved_bullets:
                    st.caption("✨ AI-improved bullet points active. You can edit them below:")

            # Display editable bullet points
            if exp.improved_bullets:
                bullets_text = "\n".join(exp.improved_bullets)
                new_bullets_text = st.text_area(
                    "Edit ATS Bullet Points (one per line):",
                    value=bullets_text,
                    key=f"exp_bullets_edit_{idx}",
                    height=120,
                )
                exp.improved_bullets = [b.strip() for b in new_bullets_text.split("\n") if b.strip()]

            if len(res.experience) > 1:
                if st.button("🗑️ Remove Experience", key=f"del_exp_{idx}"):
                    to_remove_exp = idx

    if to_remove_exp is not None:
        res.experience.pop(to_remove_exp)
        st.rerun()

    if st.button("➕ Add Another Experience"):
        res.experience.append(ExperienceEntry())
        st.rerun()


# ==========================================
# TAB 6: Projects
# ==========================================
with tabs[5]:
    st.subheader("Technical Projects")
    st.caption("Showcase hands-on software development, open-source repositories, and system design experience.")

    if not res.projects:
        res.projects.append(ProjectEntry())

    to_remove_proj = None
    for idx, proj in enumerate(res.projects):
        with st.expander(f"🚀 Project #{idx + 1}: {proj.name or 'New Project'}", expanded=True):
            pc1, pc2 = st.columns(2)
            with pc1:
                proj.name = st.text_input("Project Name *", value=proj.name, key=f"pname_{idx}")
                raw_tech = st.text_input(
                    "Technologies Used (comma-separated)",
                    value=", ".join(proj.technologies),
                    key=f"ptech_{idx}",
                    placeholder="Python, Streamlit, Ollama, PostgreSQL",
                )
                proj.technologies = split_lines_or_commas(raw_tech)

            with pc2:
                proj.github_url = st.text_input("GitHub Repository URL", value=proj.github_url, key=f"pgh_{idx}")
                proj.demo_url = st.text_input("Live Demo URL", value=proj.demo_url, key=f"pdemo_{idx}")

            proj.description = st.text_area(
                "Project Overview (What does this system do?)",
                value=proj.description,
                key=f"pdesc_{idx}",
                placeholder="e.g. A local semantic search engine that ingests PDF documents and answers questions...",
                height=80,
            )
            proj.key_contributions = st.text_area(
                "Your Specific Contributions & Architecture Decisions",
                value=proj.key_contributions,
                key=f"pcontrib_{idx}",
                placeholder="e.g. Implemented the RAG vector indexing pipeline. Built the UI in Streamlit.",
                height=80,
            )

            # AI Project Improvement
            p_col_btn, p_col_stat = st.columns([1, 3])
            with p_col_btn:
                if st.button("⚡ Improve with AI", key=f"btn_ai_proj_{idx}", disabled=not is_online):
                    if not proj.description.strip() and not proj.key_contributions.strip():
                        st.warning("Please provide a project description or contributions first.")
                    else:
                        with st.spinner("Generating technical ATS bullets..."):
                            try:
                                bullets = improve_project_bullets(proj, res.target_job, ai_client)
                                proj.improved_bullets = bullets
                                st.success("Project bullets generated!")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")

            if proj.improved_bullets:
                bullets_text = "\n".join(proj.improved_bullets)
                new_proj_bullets = st.text_area(
                    "Edit Project Bullets (one per line):",
                    value=bullets_text,
                    key=f"proj_bullets_edit_{idx}",
                    height=100,
                )
                proj.improved_bullets = [b.strip() for b in new_proj_bullets.split("\n") if b.strip()]

            if len(res.projects) > 1:
                if st.button("🗑️ Remove Project", key=f"del_proj_{idx}"):
                    to_remove_proj = idx

    if to_remove_proj is not None:
        res.projects.pop(to_remove_proj)
        st.rerun()

    if st.button("➕ Add Another Project"):
        res.projects.append(ProjectEntry())
        st.rerun()


# ==========================================
# TAB 7: Certifications & Honors
# ==========================================
with tabs[6]:
    st.subheader("Certifications")
    if not res.certifications:
        res.certifications.append(CertificationEntry())

    to_del_cert = None
    for idx, cert in enumerate(res.certifications):
        cc1, cc2, cc3, cc4, cc5 = st.columns([3, 3, 2, 3, 1])
        with cc1:
            cert.name = st.text_input("Certification Name", value=cert.name, key=f"cname_{idx}", placeholder="AWS Certified Cloud Practitioner")
        with cc2:
            cert.issuer = st.text_input("Issuer", value=cert.issuer, key=f"ciss_{idx}", placeholder="Amazon Web Services")
        with cc3:
            cert.issue_date = st.text_input("Date", value=cert.issue_date, key=f"cdate_{idx}", placeholder="Nov 2023")
        with cc4:
            cert.credential_url = st.text_input("URL (Optional)", value=cert.credential_url, key=f"curl_{idx}")
        with cc5:
            st.write("")
            st.write("")
            if st.button("🗑️", key=f"del_c_{idx}"):
                to_del_cert = idx

    if to_del_cert is not None:
        res.certifications.pop(to_del_cert)
        st.rerun()

    if st.button("➕ Add Certification"):
        res.certifications.append(CertificationEntry())
        st.rerun()

    st.divider()

    st.subheader("Honors, Awards & Achievements")
    if not res.achievements:
        res.achievements.append(AchievementEntry())

    to_del_ach = None
    for idx, ach in enumerate(res.achievements):
        ac1, ac2, ac3, ac4 = st.columns([3, 2, 2, 1])
        with ac1:
            ach.title = st.text_input("Award / Honor Title", value=ach.title, key=f"atitle_{idx}", placeholder="1st Place — Campus Hackathon")
        with ac2:
            ach.issuer_or_event = st.text_input("Event / Organizer", value=ach.issuer_or_event, key=f"aevent_{idx}", placeholder="ACM Student Chapter")
        with ac3:
            ach.date = st.text_input("Date", value=ach.date, key=f"adate_{idx}", placeholder="Mar 2024")
        with ac4:
            st.write("")
            st.write("")
            if st.button("🗑️", key=f"del_a_{idx}"):
                to_del_ach = idx

        ach.description = st.text_input(
            "Brief Description (Optional)",
            value=ach.description,
            key=f"adesc_{idx}",
            placeholder="Built an accessible campus navigation tool with a 4-person team.",
        )

    if to_del_ach is not None:
        res.achievements.pop(to_del_ach)
        st.rerun()

    if st.button("➕ Add Achievement"):
        res.achievements.append(AchievementEntry())
        st.rerun()


# ==========================================
# TAB 8: Job Matcher & ATS Scoring
# ==========================================
with tabs[7]:
    st.subheader("Target Job & ATS Optimizer")
    st.caption("Paste a target job posting. The analyzer verifies keyword alignment, identifies gaps, and calculates a defensible ATS readiness score.")

    c_tj1, c_tj2 = st.columns([1, 2])
    with c_tj1:
        res.target_job.title = st.text_input(
            "Target Job Title",
            value=res.target_job.title,
            placeholder="e.g. Software Engineering Intern",
        )
    with c_tj2:
        res.target_job.job_description = st.text_area(
            "Target Job Posting / Description",
            value=res.target_job.job_description,
            height=120,
            placeholder="Paste requirements, responsibilities, and tech stack from LinkedIn or job board...",
        )

    st.divider()

    # Calculate ATS Score & Match
    score_data = calculate_ats_score(res)
    total_score = score_data["total_score"]
    breakdown = score_data["breakdown"]

    sc_col1, sc_col2 = st.columns([1, 2])
    with sc_col1:
        st.markdown(
            f"""
            <div class="ats-metric-card">
                <div style="font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; opacity: 0.85;">Heuristic ATS Score</div>
                <div class="ats-score-display">{total_score} <span style="font-size: 1.5rem; color: #94a3b8;">/ 100</span></div>
                <div style="font-weight: 600; font-size: 1rem;">{score_data['rating']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with sc_col2:
        st.write("**Scoring Methodology Breakdown:**")
        st.write(f"- 📋 **Section Completeness:** {breakdown['completeness']['score']} / 25 pts")
        st.write(f"- ⚡ **Action Verbs & Impact:** {breakdown['action_verbs']['score']} / 25 pts")
        st.write(f"- 🛠️ **Technical Skill Depth:** {breakdown['skills_depth']['score']} / 25 pts")
        st.write(f"- 🔤 **Contact & Format Hygiene:** {breakdown['hygiene']['score']} / 25 pts")

        # Display any actionable notes
        all_notes = (
            breakdown["completeness"]["notes"]
            + breakdown["action_verbs"]["notes"]
            + breakdown["skills_depth"]["notes"]
            + breakdown["hygiene"]["notes"]
        )
        if all_notes:
            st.info("💡 **Recommended Improvements:**\n" + "\n".join([f"- {note}" for note in all_notes]))

    # Job Matching Analysis
    if res.target_job.job_description.strip():
        st.divider()
        st.subheader("🎯 Job Description Keyword Match")

        match_results = match_resume_with_job(res, res.target_job.job_description)
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.write(f"✅ **Matching Skills ({len(match_results['matching_skills'])}):**")
            if match_results["matching_skills"]:
                chips = " ".join([f"`{s}`" for s in match_results["matching_skills"]])
                st.markdown(chips)
            else:
                st.caption("No direct keyword matches found yet.")

        with m_col2:
            st.write(f"🔍 **Missing / Not Evidenced in Resume ({len(match_results['missing_skills'])}):**")
            if match_results["missing_skills"]:
                chips = " ".join([f"`{s}`" for s in match_results["missing_skills"]])
                st.markdown(chips)
                st.caption("⚠️ *Rule: Only add these skills if you genuinely possess them! Never fabricate qualifications.*")
            else:
                st.caption("Great coverage! All detected core skills are represented.")

    if st.button("🤖 Run Deep AI Resume Audit", disabled=not is_online):
        with st.spinner("Auditing resume against ATS standards using AI..."):
            audit = analyze_resume_with_ai(res, ai_client)
            st.write("### 🔍 AI Audit Findings")

            ac1, ac2 = st.columns(2)
            with ac1:
                st.success("**Strengths Identified:**\n" + "\n".join([f"- {s}" for s in audit.get("strengths", [])]))
                st.warning("**Areas for Improvement:**\n" + "\n".join([f"- {w}" for w in audit.get("weaknesses", [])]))
            with ac2:
                st.info("**Tailoring Recommendations:**\n" + "\n".join([f"- {t}" for t in audit.get("tailoring_advice", [])]))
                st.write("**Formatting Risk Assessment:**")
                st.write("\n".join([f"- {f}" for f in audit.get("formatting_risks", [])]))


# ==========================================
# TAB 9: Live Preview & Export
# ==========================================
with tabs[8]:
    st.subheader("Live ATS Resume Preview & Export")
    st.caption(f"Template active: **{res.selected_template}** • Format: ATS Single-Column")

    # Action Bar for Downloads
    candidate_name = res.personal_info.full_name or "Candidate"
    pdf_filename = generate_resume_filename(candidate_name, "pdf")
    docx_filename = generate_resume_filename(candidate_name, "docx")

    d_col1, d_col2, d_col3 = st.columns([1, 1, 2])
    with d_col1:
        try:
            pdf_bytes = generate_resume_pdf(res)
            st.download_button(
                label="📥 Download PDF",
                data=pdf_bytes,
                file_name=pdf_filename,
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"PDF Error: {e}")

    with d_col2:
        try:
            docx_bytes = generate_resume_docx(res)
            st.download_button(
                label="📥 Download Word (DOCX)",
                data=docx_bytes,
                file_name=docx_filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"DOCX Error: {e}")

    with d_col3:
        st.caption(f"Files: `{pdf_filename}` • `{docx_filename}`")

    st.divider()

    # Rendered HTML Preview
    preview_html = render_resume_html(res)
    st.markdown(preview_html, unsafe_allow_html=True)

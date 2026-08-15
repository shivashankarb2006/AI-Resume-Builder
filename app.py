import streamlit as st

from resume_generator import generate_resume
from docx_generator import create_docx
from pdf_generator import create_pdf
from ats_analyzer import analyze_resume

from profile_manager import (
    load_all_profiles,
    save_profile,
    get_profile,
    delete_profile
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Resume Builder",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "resume": "",
    "template": "Classic ATS",
    "current_page": "Dashboard",
    "ats_analysis": None,
    "job_description": ""
}

for key, value in defaults.items():

    if key not in st.session_state:

        st.session_state[key] = value


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .main-subtitle {
        font-size: 18px;
        margin-bottom: 25px;
    }

    .feature-card {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.25);
        margin-bottom: 10px;
    }

    .stat-card {
        padding: 18px;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.25);
        text-align: center;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

with st.sidebar:

    st.title("📄 AI Resume Builder")

    st.caption(
        "Build smarter. Apply better."
    )

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Resume Builder",
            "ATS Analyzer",
            "Saved Profiles"
        ],
        index=[
            "Dashboard",
            "Resume Builder",
            "ATS Analyzer",
            "Saved Profiles"
        ].index(st.session_state["current_page"])
    )

    st.session_state["current_page"] = page

    st.divider()

    st.subheader("Features")

    st.write("🤖 AI Resume Generation")
    st.write("🎯 ATS Analysis")
    st.write("📄 PDF & DOCX")
    st.write("🎨 Resume Templates")
    st.write("💾 Saved Profiles")

    st.divider()

    st.caption(
        "Python • Streamlit • Ollama"
    )


# =========================================================
# HELPER FUNCTION
# =========================================================

def collect_resume_data():

    projects = []

    number_of_projects = int(
        st.session_state.get(
            "number_of_projects",
            3
        )
    )

    for i in range(number_of_projects):

        projects.append(
            {
                "name": st.session_state.get(
                    f"project_name_{i}",
                    ""
                ),

                "technologies": st.session_state.get(
                    f"project_technologies_{i}",
                    ""
                ),

                "description": st.session_state.get(
                    f"project_description_{i}",
                    ""
                ),

                "link": st.session_state.get(
                    f"project_link_{i}",
                    ""
                )
            }
        )


    experiences = []

    number_of_experiences = int(
        st.session_state.get(
            "number_of_experiences",
            0
        )
    )

    for i in range(number_of_experiences):

        experiences.append(
            {
                "company": st.session_state.get(
                    f"company_{i}",
                    ""
                ),

                "role": st.session_state.get(
                    f"role_{i}",
                    ""
                ),

                "start_date": st.session_state.get(
                    f"start_date_{i}",
                    ""
                ),

                "end_date": st.session_state.get(
                    f"end_date_{i}",
                    ""
                ),

                "responsibilities": st.session_state.get(
                    f"responsibilities_{i}",
                    ""
                )
            }
        )


    return {

        "name": st.session_state.get(
            "name",
            ""
        ),

        "email": st.session_state.get(
            "email",
            ""
        ),

        "phone": st.session_state.get(
            "phone",
            ""
        ),

        "location": st.session_state.get(
            "location",
            ""
        ),

        "linkedin": st.session_state.get(
            "linkedin",
            ""
        ),

        "github": st.session_state.get(
            "github",
            ""
        ),

        "objective": st.session_state.get(
            "objective",
            ""
        ),

        "education": st.session_state.get(
            "education",
            ""
        ),

        "skills": st.session_state.get(
            "skills",
            ""
        ),

        "projects": projects,

        "experiences": experiences,

        "certifications": st.session_state.get(
            "certifications",
            ""
        ),

        "achievements": st.session_state.get(
            "achievements",
            ""
        ),

        "languages": st.session_state.get(
            "languages",
            ""
        )
    }


# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    st.markdown(
        '<div class="main-title">'
        'Welcome to AI Resume Builder 👋'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="main-subtitle">'
        'Create an ATS-friendly resume, analyze job matches, '
        'and download your resume in professional formats.'
        '</div>',
        unsafe_allow_html=True
    )


    # -----------------------------------------------------
    # STATS
    # -----------------------------------------------------

    profiles = load_all_profiles()

    stat1, stat2, stat3, stat4 = st.columns(4)


    with stat1:

        st.metric(
            "Saved Profiles",
            len(profiles)
        )


    with stat2:

        if st.session_state["resume"]:

            st.metric(
                "Resume Status",
                "Ready"
            )

        else:

            st.metric(
                "Resume Status",
                "Not Created"
            )


    with stat3:

        if st.session_state["ats_analysis"]:

            score = st.session_state[
                "ats_analysis"
            ].get(
                "score",
                0
            )

            st.metric(
                "ATS Score",
                f"{score}/100"
            )

        else:

            st.metric(
                "ATS Score",
                "-"
            )


    with stat4:

        st.metric(
            "Templates",
            "3"
        )


    st.divider()


    # -----------------------------------------------------
    # QUICK ACTIONS
    # -----------------------------------------------------

    st.header("Quick Actions")

    action1, action2, action3 = st.columns(3)


    with action1:

        st.markdown(
            """
            <div class="feature-card">

            ### 📝 Build Resume

            Enter your education, skills,
            projects and experience.

            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "Open Resume Builder",
            use_container_width=True
        ):

            st.session_state[
                "current_page"
            ] = "Resume Builder"

            st.rerun()


    with action2:

        st.markdown(
            """
            <div class="feature-card">

            ### 🎯 Check ATS Score

            Compare your resume with
            a real job description.

            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "Open ATS Analyzer",
            use_container_width=True
        ):

            st.session_state[
                "current_page"
            ] = "ATS Analyzer"

            st.rerun()


    with action3:

        st.markdown(
            """
            <div class="feature-card">

            ### 💾 Saved Profiles

            Quickly load previously saved
            resume information.

            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "Open Saved Profiles",
            use_container_width=True
        ):

            st.session_state[
                "current_page"
            ] = "Saved Profiles"

            st.rerun()


    st.divider()


    # -----------------------------------------------------
    # HOW IT WORKS
    # -----------------------------------------------------

    st.header("How It Works")

    step1, step2, step3, step4 = st.columns(4)


    with step1:

        st.markdown(
            """
            ### 1️⃣ Enter Details

            Add your real education,
            skills, projects and experience.
            """
        )


    with step2:

        st.markdown(
            """
            ### 2️⃣ Generate

            Local AI converts your
            information into an ATS-friendly resume.
            """
        )


    with step3:

        st.markdown(
            """
            ### 3️⃣ Analyze

            Compare the resume against
            a job description.
            """
        )


    with step4:

        st.markdown(
            """
            ### 4️⃣ Download

            Download your professional
            PDF or DOCX resume.
            """
        )


# =========================================================
# RESUME BUILDER
# =========================================================

elif page == "Resume Builder":

    st.title("📝 Resume Builder")

    st.write(
        "Enter your information below."
    )

    st.divider()


    # -----------------------------------------------------
    # PERSONAL INFORMATION
    # -----------------------------------------------------

    st.header("Personal Information")

    col1, col2 = st.columns(2)


    with col1:

        st.text_input(
            "Full Name",
            placeholder="Your full name",
            key="name"
        )

        st.text_input(
            "Email",
            placeholder="yourname@gmail.com",
            key="email"
        )

        st.text_input(
            "Phone Number",
            placeholder="+91 9876543210",
            key="phone"
        )


    with col2:

        st.text_input(
            "Location",
            placeholder="Bengaluru, Karnataka",
            key="location"
        )

        st.text_input(
            "LinkedIn URL",
            placeholder="https://linkedin.com/in/yourname",
            key="linkedin"
        )

        st.text_input(
            "GitHub URL",
            placeholder="https://github.com/yourusername",
            key="github"
        )


    # -----------------------------------------------------
    # OBJECTIVE
    # -----------------------------------------------------

    st.header("Career Objective")

    st.text_area(
        "Career Objective",
        height=100,
        placeholder=(
            "Describe your career goals."
        ),
        key="objective"
    )


    # -----------------------------------------------------
    # EDUCATION
    # -----------------------------------------------------

    st.header("Education")

    st.text_area(
        "Education Details",
        height=130,
        placeholder="""B.E. Information Science and Engineering
College Name
2024 - 2028
CGPA: 8.2""",
        key="education"
    )


    # -----------------------------------------------------
    # SKILLS
    # -----------------------------------------------------

    st.header("Technical Skills")

    st.text_area(
        "Technical Skills",
        height=90,
        placeholder=(
            "Python, Java, C, SQL, Machine Learning, "
            "Pandas, NumPy, Git, GitHub"
        ),
        key="skills"
    )


    # -----------------------------------------------------
    # PROJECTS
    # -----------------------------------------------------

    st.header("Projects")

    st.number_input(
        "Number of Projects",
        min_value=1,
        max_value=6,
        value=3,
        step=1,
        key="number_of_projects"
    )

    project_count = int(
        st.session_state[
            "number_of_projects"
        ]
    )


    for i in range(project_count):

        st.subheader(
            f"Project {i + 1}"
        )

        c1, c2 = st.columns(2)


        with c1:

            st.text_input(
                "Project Name",
                key=f"project_name_{i}"
            )


        with c2:

            st.text_input(
                "Technologies",
                key=f"project_technologies_{i}"
            )


        st.text_area(
            "Description",
            height=90,
            key=f"project_description_{i}"
        )


        st.text_input(
            "GitHub / Project Link",
            key=f"project_link_{i}"
        )


    # -----------------------------------------------------
    # EXPERIENCE
    # -----------------------------------------------------

    st.header(
        "Experience / Internships"
    )

    st.number_input(
        "Number of Experiences",
        min_value=0,
        max_value=5,
        value=0,
        step=1,
        key="number_of_experiences"
    )

    experience_count = int(
        st.session_state[
            "number_of_experiences"
        ]
    )


    for i in range(experience_count):

        st.subheader(
            f"Experience {i + 1}"
        )

        c1, c2 = st.columns(2)


        with c1:

            st.text_input(
                "Company",
                key=f"company_{i}"
            )

            st.text_input(
                "Role",
                key=f"role_{i}"
            )


        with c2:

            st.text_input(
                "Start Date",
                key=f"start_date_{i}"
            )

            st.text_input(
                "End Date",
                key=f"end_date_{i}"
            )


        st.text_area(
            "Responsibilities",
            height=100,
            key=f"responsibilities_{i}"
        )


    # -----------------------------------------------------
    # OTHER INFORMATION
    # -----------------------------------------------------

    st.header("Additional Information")

    st.text_area(
        "Certifications",
        height=100,
        key="certifications"
    )

    st.text_area(
        "Achievements",
        height=100,
        key="achievements"
    )

    st.text_input(
        "Languages",
        placeholder="English, Kannada, Hindi",
        key="languages"
    )


    # -----------------------------------------------------
    # TEMPLATE
    # -----------------------------------------------------

    st.header(
        "Resume Template"
    )

    st.radio(
        "Choose a template",
        [
            "Classic ATS",
            "Modern Professional",
            "Minimal Student"
        ],
        index=0,
        key="template_selector"
    )


    # -----------------------------------------------------
    # SAVE PROFILE
    # -----------------------------------------------------

    st.divider()

    st.header(
        "Save Resume Profile"
    )

    profile_name = st.text_input(
        "Profile Name",
        placeholder="Example: Machine Learning Resume",
        key="profile_name"
    )


    if st.button(
        "💾 Save Profile",
        use_container_width=True
    ):

        if not profile_name.strip():

            st.error(
                "Please enter a profile name."
            )

        else:

            resume_data = collect_resume_data()

            save_profile(
                profile_name.strip(),
                resume_data
            )

            st.success(
                f"Profile '{profile_name}' saved!"
            )


    # -----------------------------------------------------
    # GENERATE
    # -----------------------------------------------------

    st.divider()

    if st.button(
        "🚀 Generate AI Resume",
        type="primary",
        use_container_width=True
    ):

        resume_data = collect_resume_data()

        if not resume_data["name"].strip():

            st.error(
                "Please enter your full name."
            )

        elif not resume_data["email"].strip():

            st.error(
                "Please enter your email."
            )

        elif not resume_data["skills"].strip():

            st.error(
                "Please enter your technical skills."
            )

        else:

            with st.spinner(
                "AI is creating your resume..."
            ):

                try:

                    resume = generate_resume(
                        resume_data
                    )

                    st.session_state[
                        "resume"
                    ] = resume

                    st.session_state[
                        "template"
                    ] = st.session_state[
                        "template_selector"
                    ]

                    st.success(
                        "Resume generated successfully!"
                    )

                except Exception as error:

                    st.error(
                        "Resume generation failed."
                    )

                    st.code(
                        str(error)
                    )


    # -----------------------------------------------------
    # PREVIEW
    # -----------------------------------------------------

    if st.session_state["resume"]:

        st.divider()

        st.header(
            "📄 Generated Resume"
        )

        st.text_area(
            "Resume Preview",
            st.session_state["resume"],
            height=650
        )


        selected_template = st.session_state[
            "template"
        ]


        # -------------------------------------------------
        # DOWNLOAD
        # -------------------------------------------------

        st.subheader(
            "Download"
        )

        d1, d2 = st.columns(2)


        with d1:

            try:

                docx_file = create_docx(
                    st.session_state["resume"],
                    selected_template
                )

                with open(
                    docx_file,
                    "rb"
                ) as file:

                    st.download_button(
                        "📘 Download DOCX",
                        data=file,
                        file_name="AI_Resume.docx",
                        mime=(
                            "application/vnd.openxmlformats-officedocument."
                            "wordprocessingml.document"
                        ),
                        use_container_width=True
                    )

            except Exception as error:

                st.error(
                    "DOCX generation failed."
                )

                st.code(
                    str(error)
                )


        with d2:

            try:

                pdf_file = create_pdf(
                    st.session_state["resume"],
                    selected_template
                )

                with open(
                    pdf_file,
                    "rb"
                ) as file:

                    st.download_button(
                        "📕 Download PDF",
                        data=file,
                        file_name="AI_Resume.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

            except Exception as error:

                st.error(
                    "PDF generation failed."
                )

                st.code(
                    str(error)
                )


# =========================================================
# ATS ANALYZER
# =========================================================

elif page == "ATS Analyzer":

    st.title("🎯 ATS Resume Analyzer")

    if not st.session_state["resume"]:

        st.warning(
            "Generate a resume first from the Resume Builder."
        )

        if st.button(
            "Open Resume Builder"
        ):

            st.session_state[
                "current_page"
            ] = "Resume Builder"

            st.rerun()

    else:

        st.success(
            "Resume loaded and ready for analysis."
        )

        st.text_area(
            "Current Resume",
            st.session_state["resume"],
            height=400
        )

        st.subheader(
            "Job Description"
        )

        job_description = st.text_area(
            "Paste the job description",
            height=250,
            placeholder=(
                "Paste the complete job description here..."
            ),
            key="job_description"
        )


        if st.button(
            "🔍 Analyze ATS Match",
            type="primary",
            use_container_width=True
        ):

            if not job_description.strip():

                st.warning(
                    "Please paste a job description."
                )

            else:

                with st.spinner(
                    "AI is analyzing your resume..."
                ):

                    try:

                        analysis = analyze_resume(
                            st.session_state["resume"],
                            job_description
                        )

                        st.session_state[
                            "ats_analysis"
                        ] = analysis

                    except Exception as error:

                        st.error(
                            "ATS analysis failed."
                        )

                        st.code(
                            str(error)
                        )


        # -------------------------------------------------
        # RESULTS
        # -------------------------------------------------

        if st.session_state["ats_analysis"]:

            analysis = st.session_state[
                "ats_analysis"
            ]

            score = int(
                analysis.get(
                    "score",
                    0
                )
            )

            matching = analysis.get(
                "matching_keywords",
                []
            )

            missing = analysis.get(
                "missing_keywords",
                []
            )

            suggestions = analysis.get(
                "suggestions",
                []
            )


            st.divider()

            st.header(
                "ATS Results"
            )


            # SCORE

            st.metric(
                "ATS Compatibility Score",
                f"{score}/100"
            )

            st.progress(
                min(
                    max(score, 0),
                    100
                ) / 100
            )


            if score >= 80:

                st.success(
                    "Excellent match!"
                )

            elif score >= 60:

                st.warning(
                    "Good match. Some improvements are recommended."
                )

            else:

                st.error(
                    "Low match. Consider improving the resume "
                    "for this position."
                )


            # KEYWORDS

            c1, c2 = st.columns(2)


            with c1:

                st.subheader(
                    "✅ Matching Keywords"
                )

                if matching:

                    for keyword in matching:

                        st.write(
                            f"✓ {keyword}"
                        )

                else:

                    st.write(
                        "No matching keywords found."
                    )


            with c2:

                st.subheader(
                    "⚠️ Missing Keywords"
                )

                if missing:

                    for keyword in missing:

                        st.write(
                            f"• {keyword}"
                        )

                else:

                    st.write(
                        "No major missing keywords."
                    )


            # SUGGESTIONS

            st.subheader(
                "💡 Suggestions"
            )

            for suggestion in suggestions:

                st.write(
                    f"• {suggestion}"
                )


# =========================================================
# SAVED PROFILES
# =========================================================

elif page == "Saved Profiles":

    st.title("💾 Saved Profiles")

    profiles = load_all_profiles()


    if not profiles:

        st.info(
            "You don't have any saved profiles yet."
        )

        if st.button(
            "Create Your First Profile"
        ):

            st.session_state[
                "current_page"
            ] = "Resume Builder"

            st.rerun()

    else:

        st.write(
            f"You have **{len(profiles)}** saved profile(s)."
        )


        for profile_name in profiles:

            with st.expander(
                f"📄 {profile_name}"
            ):

                profile = get_profile(
                    profile_name
                )

                st.write(
                    f"**Name:** "
                    f"{profile.get('name', '')}"
                )

                st.write(
                    f"**Email:** "
                    f"{profile.get('email', '')}"
                )

                st.write(
                    f"**Skills:** "
                    f"{profile.get('skills', '')}"
                )

                projects = profile.get(
                    "projects",
                    []
                )

                st.write(
                    f"**Projects:** "
                    f"{len(projects)}"
                )


                c1, c2 = st.columns(2)


                with c1:

                    if st.button(
                        "📂 Load Profile",
                        key=f"load_{profile_name}",
                        use_container_width=True
                    ):

                        for key, value in profile.items():

                            st.session_state[
                                key
                            ] = value

                        st.session_state[
                            "current_page"
                        ] = "Resume Builder"

                        st.success(
                            f"Loaded '{profile_name}'."
                        )

                        st.rerun()


                with c2:

                    if st.button(
                        "🗑️ Delete",
                        key=f"delete_{profile_name}",
                        use_container_width=True
                    ):

                        delete_profile(
                            profile_name
                        )

                        st.success(
                            f"Deleted '{profile_name}'."
                        )

                        st.rerun()


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "AI Resume Builder | "
    "Python + Streamlit + Ollama | "
    "Built for ATS-friendly resume creation"
)
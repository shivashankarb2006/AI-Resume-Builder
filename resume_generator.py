from gemini_client import ask_gemini


def generate_resume(resume_data):

    name = resume_data.get("name", "")
    email = resume_data.get("email", "")
    phone = resume_data.get("phone", "")
    location = resume_data.get("location", "")
    linkedin = resume_data.get("linkedin", "")
    github = resume_data.get("github", "")

    objective = resume_data.get(
        "objective",
        ""
    )

    education = resume_data.get(
        "education",
        ""
    )

    skills = resume_data.get(
        "skills",
        ""
    )

    projects = resume_data.get(
        "projects",
        []
    )

    experiences = resume_data.get(
        "experiences",
        []
    )

    certifications = resume_data.get(
        "certifications",
        ""
    )

    achievements = resume_data.get(
        "achievements",
        ""
    )

    languages = resume_data.get(
        "languages",
        ""
    )


    # -----------------------------------------------------
    # PROJECTS
    # -----------------------------------------------------

    project_text = ""

    for project in projects:

        project_text += f"""
Project Name: {project.get("name", "")}
Technologies: {project.get("technologies", "")}
Description: {project.get("description", "")}
Link: {project.get("link", "")}
"""


    # -----------------------------------------------------
    # EXPERIENCE
    # -----------------------------------------------------

    experience_text = ""

    for experience in experiences:

        experience_text += f"""
Company: {experience.get("company", "")}
Role: {experience.get("role", "")}
Start Date: {experience.get("start_date", "")}
End Date: {experience.get("end_date", "")}
Responsibilities:
{experience.get("responsibilities", "")}
"""


    # -----------------------------------------------------
    # AI PROMPT
    # -----------------------------------------------------

    prompt = f"""
You are a professional resume writer and ATS optimization expert.

Create a professional, concise and ATS-friendly resume using ONLY
the information provided by the user.

IMPORTANT RULES:

1. Do NOT invent experience.
2. Do NOT invent education.
3. Do NOT invent certifications.
4. Do NOT invent companies.
5. Do NOT invent skills.
6. Do NOT add fake achievements.
7. Do NOT add fake numbers or statistics.
8. Do NOT add information that the user did not provide.
9. Improve wording and grammar while preserving the facts.
10. Use strong professional action verbs where appropriate.
11. Keep the resume suitable for a student/fresher if the experience
    section is limited.
12. Make the resume ATS-friendly.
13. Avoid tables.
14. Avoid graphics.
15. Avoid emojis.
16. Use simple section headings.
17. Keep formatting clean and professional.
18. Prioritize relevant technical skills and projects.
19. Do not include a References section.
20. Return ONLY the resume content.

Use this structure when relevant:

NAME

Contact Information

PROFESSIONAL SUMMARY

EDUCATION

TECHNICAL SKILLS

PROJECTS

EXPERIENCE

CERTIFICATIONS

ACHIEVEMENTS

LANGUAGES


USER INFORMATION
================

Name:
{name}

Email:
{email}

Phone:
{phone}

Location:
{location}

LinkedIn:
{linkedin}

GitHub:
{github}


CAREER OBJECTIVE
================

{objective}


EDUCATION
=========

{education}


TECHNICAL SKILLS
================

{skills}


PROJECTS
========

{project_text}


EXPERIENCE / INTERNSHIPS
========================

{experience_text}


CERTIFICATIONS
==============

{certifications}


ACHIEVEMENTS
============

{achievements}


LANGUAGES
=========

{languages}


Now create the final ATS-friendly resume.
"""


    # -----------------------------------------------------
    # SEND TO GEMINI
    # -----------------------------------------------------

    resume = ask_gemini(prompt)


    # -----------------------------------------------------
    # CLEAN RESPONSE
    # -----------------------------------------------------

    if not resume:

        raise ValueError(
            "Gemini returned an empty response."
        )


    return resume.strip()
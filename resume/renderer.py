"""
Live HTML Resume Renderer for Streamlit preview.
Generates a sanitized, beautiful, paper-like preview corresponding to the selected template.
"""
from typing import List
from models.resume_schema import ResumeData
from utils.helpers import sanitize_html
from .templates import TEMPLATE_CONFIGS, TEMPLATE_CLASSIC_ATS


def render_resume_html(resume_data: ResumeData) -> str:
    """
    Render complete sanitized HTML/CSS for in-app resume preview.
    """
    template_name = resume_data.selected_template or TEMPLATE_CLASSIC_ATS
    config = TEMPLATE_CONFIGS.get(template_name, TEMPLATE_CONFIGS[TEMPLATE_CLASSIC_ATS])

    font_family = config["font_family_html"]
    primary_color = config["primary_color"]
    heading_color = config["heading_color"]
    divider_color = config["divider_color"]
    header_align = config["header_alignment"]
    accent_color = config["accent_color"]

    p = resume_data.personal_info
    name = sanitize_html(p.full_name) or "Your Name"

    # Contact line items
    contacts = []
    if p.email:
        contacts.append(f'<a href="mailto:{sanitize_html(p.email)}" style="color: {accent_color}; text-decoration: none;">{sanitize_html(p.email)}</a>')
    if p.phone:
        contacts.append(f'<span>{sanitize_html(p.phone)}</span>')
    if p.location:
        contacts.append(f'<span>{sanitize_html(p.location)}</span>')
    if p.linkedin_url:
        contacts.append(f'<a href="{sanitize_html(p.linkedin_url)}" target="_blank" style="color: {accent_color}; text-decoration: none;">LinkedIn</a>')
    if p.github_url:
        contacts.append(f'<a href="{sanitize_html(p.github_url)}" target="_blank" style="color: {accent_color}; text-decoration: none;">GitHub</a>')
    if p.portfolio_url:
        contacts.append(f'<a href="{sanitize_html(p.portfolio_url)}" target="_blank" style="color: {accent_color}; text-decoration: none;">Portfolio</a>')

    contact_bar = " &nbsp;|&nbsp; ".join(contacts)

    sections_html = []
    enabled = resume_data.enabled_sections

    # Determine section order based on template
    section_order = config.get("section_order", [
        "Professional Summary",
        "Education",
        "Skills",
        "Experience",
        "Projects",
        "Certifications",
        "Achievements",
    ])

    for sec in section_order:
        if sec not in enabled:
            continue

        if sec == "Professional Summary" and resume_data.summary.strip():
            summary_content = sanitize_html(resume_data.summary)
            sections_html.append(f"""
            <div class="resume-section">
                <div class="section-title" style="color: {heading_color}; border-bottom: 1.5px solid {divider_color};">PROFESSIONAL SUMMARY</div>
                <p style="margin: 6px 0 0 0; line-height: 1.5; color: {primary_color}; font-size: 10.5pt;">{summary_content}</p>
            </div>
            """)

        elif sec == "Education" and resume_data.education:
            valid_edus = [e for e in resume_data.education if not e.is_empty()]
            if valid_edus:
                edu_items = []
                for e in valid_edus:
                    inst = sanitize_html(e.institution)
                    deg = sanitize_html(e.degree)
                    field = sanitize_html(e.field_of_study)
                    dates = f"{sanitize_html(e.start_year)} – {sanitize_html(e.end_year)}" if e.start_year or e.end_year else ""
                    gpa = f" | GPA: {sanitize_html(e.gpa)}" if e.gpa else ""
                    coursework = f"<div style='font-size: 9.5pt; color: #4b5563; margin-top: 2px;'><strong>Relevant Coursework:</strong> {sanitize_html(e.relevant_coursework)}</div>" if e.relevant_coursework else ""

                    degree_line = f"{deg} in {field}{gpa}" if field else f"{deg}{gpa}"
                    edu_items.append(f"""
                    <div style="margin-top: 8px;">
                        <div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 11pt; color: {heading_color};">
                            <span>{inst}</span>
                            <span>{dates}</span>
                        </div>
                        <div style="font-size: 10.5pt; color: {primary_color};">{degree_line}</div>
                        {coursework}
                    </div>
                    """)
                sections_html.append(f"""
                <div class="resume-section">
                    <div class="section-title" style="color: {heading_color}; border-bottom: 1.5px solid {divider_color};">EDUCATION</div>
                    {''.join(edu_items)}
                </div>
                """)

        elif sec == "Skills" and not resume_data.skills.is_empty():
            s = resume_data.skills
            skill_lines = []
            if s.programming_languages:
                skill_lines.append(f"<div><strong>Languages:</strong> {sanitize_html(', '.join(s.programming_languages))}</div>")
            if s.frameworks:
                skill_lines.append(f"<div><strong>Frameworks / Libraries:</strong> {sanitize_html(', '.join(s.frameworks))}</div>")
            if s.tools:
                skill_lines.append(f"<div><strong>Developer Tools:</strong> {sanitize_html(', '.join(s.tools))}</div>")
            if s.ai_ml:
                skill_lines.append(f"<div><strong>AI / Machine Learning:</strong> {sanitize_html(', '.join(s.ai_ml))}</div>")
            if s.databases:
                skill_lines.append(f"<div><strong>Databases:</strong> {sanitize_html(', '.join(s.databases))}</div>")
            for c in s.custom_categories:
                if c.category_name.strip() and c.skills:
                    skill_lines.append(f"<div><strong>{sanitize_html(c.category_name)}:</strong> {sanitize_html(', '.join(c.skills))}</div>")

            sections_html.append(f"""
            <div class="resume-section">
                <div class="section-title" style="color: {heading_color}; border-bottom: 1.5px solid {divider_color};">TECHNICAL SKILLS</div>
                <div style="margin-top: 6px; font-size: 10.5pt; line-height: 1.6; color: {primary_color};">
                    {''.join(skill_lines)}
                </div>
            </div>
            """)

        elif sec == "Experience" and resume_data.experience:
            valid_exps = [e for e in resume_data.experience if not e.is_empty()]
            if valid_exps:
                exp_items = []
                for e in valid_exps:
                    comp = sanitize_html(e.company)
                    role = sanitize_html(e.role)
                    loc = sanitize_html(e.location)
                    dates = f"{sanitize_html(e.start_date)} – {'Present' if e.is_current else sanitize_html(e.end_date)}"

                    # Bullets preference: improved_bullets first, else split lines
                    bullets = e.improved_bullets
                    if not bullets and e.responsibilities:
                        bullets = [b.strip() for b in e.responsibilities.split("\n") if b.strip()]

                    bullet_html = "".join([f"<li style='margin-bottom: 4px;'>{sanitize_html(b)}</li>" for b in bullets])

                    exp_items.append(f"""
                    <div style="margin-top: 8px;">
                        <div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 11pt; color: {heading_color};">
                            <span>{comp} <span style="font-weight: normal; font-size: 10.5pt; color: #4b5563;">— {loc}</span></span>
                            <span>{dates}</span>
                        </div>
                        <div style="font-style: italic; font-size: 10.5pt; color: {primary_color}; margin-bottom: 4px;">{role}</div>
                        <ul style="margin: 0; padding-left: 20px; font-size: 10pt; line-height: 1.45; color: {primary_color};">
                            {bullet_html}
                        </ul>
                    </div>
                    """)
                sections_html.append(f"""
                <div class="resume-section">
                    <div class="section-title" style="color: {heading_color}; border-bottom: 1.5px solid {divider_color};">PROFESSIONAL EXPERIENCE</div>
                    {''.join(exp_items)}
                </div>
                """)

        elif sec == "Projects" and resume_data.projects:
            valid_projs = [p for p in resume_data.projects if not p.is_empty()]
            if valid_projs:
                proj_items = []
                for p_entry in valid_projs:
                    pname = sanitize_html(p_entry.name)
                    tech = f" | <em>{sanitize_html(', '.join(p_entry.technologies))}</em>" if p_entry.technologies else ""
                    links = []
                    if p_entry.github_url:
                        links.append(f'<a href="{sanitize_html(p_entry.github_url)}" target="_blank" style="color: {accent_color}; text-decoration: none;">GitHub</a>')
                    if p_entry.demo_url:
                        links.append(f'<a href="{sanitize_html(p_entry.demo_url)}" target="_blank" style="color: {accent_color}; text-decoration: none;">Live Demo</a>')
                    link_str = f" ({' | '.join(links)})" if links else ""

                    bullets = p_entry.improved_bullets
                    if not bullets and p_entry.key_contributions:
                        bullets = [b.strip() for b in p_entry.key_contributions.split("\n") if b.strip()]
                    elif not bullets and p_entry.description:
                        bullets = [p_entry.description]

                    bullet_html = "".join([f"<li style='margin-bottom: 4px;'>{sanitize_html(b)}</li>" for b in bullets])

                    proj_items.append(f"""
                    <div style="margin-top: 8px;">
                        <div style="font-size: 11pt; color: {heading_color}; font-weight: bold;">
                            <span>{pname}</span>{tech}{link_str}
                        </div>
                        <ul style="margin: 4px 0 0 0; padding-left: 20px; font-size: 10pt; line-height: 1.45; color: {primary_color};">
                            {bullet_html}
                        </ul>
                    </div>
                    """)
                sections_html.append(f"""
                <div class="resume-section">
                    <div class="section-title" style="color: {heading_color}; border-bottom: 1.5px solid {divider_color};">TECHNICAL PROJECTS</div>
                    {''.join(proj_items)}
                </div>
                """)

        elif sec == "Certifications" and resume_data.certifications:
            valid_certs = [c for c in resume_data.certifications if not c.is_empty()]
            if valid_certs:
                cert_items = []
                for c in valid_certs:
                    cname = sanitize_html(c.name)
                    issuer = f" — {sanitize_html(c.issuer)}" if c.issuer else ""
                    date = f" ({sanitize_html(c.issue_date)})" if c.issue_date else ""
                    link = f' [<a href="{sanitize_html(c.credential_url)}" target="_blank" style="color: {accent_color}; text-decoration: none;">Credential</a>]' if c.credential_url else ""
                    cert_items.append(f"<li style='margin-bottom: 4px;'><strong>{cname}</strong>{issuer}{date}{link}</li>")
                sections_html.append(f"""
                <div class="resume-section">
                    <div class="section-title" style="color: {heading_color}; border-bottom: 1.5px solid {divider_color};">CERTIFICATIONS</div>
                    <ul style="margin: 6px 0 0 0; padding-left: 20px; font-size: 10pt; line-height: 1.45; color: {primary_color};">
                        {''.join(cert_items)}
                    </ul>
                </div>
                """)

        elif sec == "Achievements" and resume_data.achievements:
            valid_achs = [a for a in resume_data.achievements if not a.is_empty()]
            if valid_achs:
                ach_items = []
                for a in valid_achs:
                    title = sanitize_html(a.title)
                    ev = f" | {sanitize_html(a.issuer_or_event)}" if a.issuer_or_event else ""
                    dt = f" ({sanitize_html(a.date)})" if a.date else ""
                    desc = f": {sanitize_html(a.description)}" if a.description else ""
                    ach_items.append(f"<li style='margin-bottom: 4px;'><strong>{title}</strong>{ev}{dt}{desc}</li>")
                sections_html.append(f"""
                <div class="resume-section">
                    <div class="section-title" style="color: {heading_color}; border-bottom: 1.5px solid {divider_color};">HONORS & ACHIEVEMENTS</div>
                    <ul style="margin: 6px 0 0 0; padding-left: 20px; font-size: 10pt; line-height: 1.45; color: {primary_color};">
                        {''.join(ach_items)}
                    </ul>
                </div>
                """)

        elif sec == "Volunteer Experience" and resume_data.volunteer:
            valid_vols = [v for v in resume_data.volunteer if not v.is_empty()]
            if valid_vols:
                vol_items = []
                for v in valid_vols:
                    org = sanitize_html(v.organization)
                    vrole = sanitize_html(v.role)
                    vdates = f" ({sanitize_html(v.dates)})" if v.dates else ""
                    vdetails = f": {sanitize_html(v.details)}" if v.details else ""
                    vol_items.append(f"<li style='margin-bottom: 4px;'><strong>{vrole}</strong> at {org}{vdates}{vdetails}</li>")
                sections_html.append(f"""
                <div class="resume-section">
                    <div class="section-title" style="color: {heading_color}; border-bottom: 1.5px solid {divider_color};">VOLUNTEER & LEADERSHIP</div>
                    <ul style="margin: 6px 0 0 0; padding-left: 20px; font-size: 10pt; line-height: 1.45; color: {primary_color};">
                        {''.join(vol_items)}
                    </ul>
                </div>
                """)

    html_document = f"""
    <div style="font-family: {font_family}; background: #ffffff; color: {primary_color}; padding: 36px 44px; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.06); max-width: 820px; margin: 0 auto; box-sizing: border-box;">
        <style>
            .resume-section {{ margin-top: 14px; }}
            .section-title {{
                font-size: 11.5pt;
                font-weight: bold;
                letter-spacing: 0.8px;
                padding-bottom: 3px;
                margin-bottom: 4px;
                text-transform: uppercase;
            }}
        </style>
        <!-- Header -->
        <div style="text-align: {header_align}; margin-bottom: 12px;">
            <h1 style="margin: 0; font-size: 22pt; font-weight: bold; color: {heading_color}; letter-spacing: -0.3px;">{name}</h1>
            <div style="margin-top: 6px; font-size: 9.5pt; color: #4b5563; line-height: 1.4;">
                {contact_bar}
            </div>
        </div>

        <!-- Sections -->
        {''.join(sections_html)}
    </div>
    """
    return html_document

"""
AI Resume Builder - Resume Generation & Multi-Format Rendering Engine
Formats structured resume data into Markdown, ATS Plain Text, and Printable HTML.
"""

import os
import html
from typing import Dict, Any, Tuple, Optional
from jinja2 import Template

from src.validators import validate_profile
from src.prompts import RESUME_SYSTEM_PROMPT, build_resume_generation_prompt
from src.claude_api import get_api_key, call_claude_json, get_mock_resume_data


def format_resume_text(resume: Dict[str, Any]) -> str:
    """
    Format resume into pure, unformatted ATS plain text.
    Ideal for pasting into ATS application text fields.
    """
    lines = []
    p = resume.get("personal_info", {})

    # Header
    if p.get("full_name"):
        lines.append(p["full_name"].upper())
    if p.get("professional_title"):
        lines.append(p["professional_title"])

    contact = [
        p.get("email"),
        p.get("phone"),
        p.get("location"),
        p.get("linkedin"),
        p.get("github"),
        p.get("portfolio"),
    ]
    lines.append(" | ".join([c for c in contact if c]))
    lines.append("\n" + "=" * 60 + "\n")

    # Summary
    if resume.get("professional_summary"):
        lines.append("PROFESSIONAL SUMMARY")
        lines.append("-" * 30)
        lines.append(resume["professional_summary"])
        lines.append("\n")

    # Skills
    if resume.get("skills"):
        lines.append("TECHNICAL SKILLS")
        lines.append("-" * 30)
        for cat, items in resume["skills"].items():
            cat_name = cat.replace("_", " ").title()
            if isinstance(items, list) and items:
                lines.append(f"{cat_name}: {', '.join(items)}")
            elif isinstance(items, str) and items:
                lines.append(f"{cat_name}: {items}")
        lines.append("\n")

    # Experience
    if resume.get("experience"):
        lines.append("WORK EXPERIENCE")
        lines.append("-" * 30)
        for exp in resume["experience"]:
            lines.append(f"{exp.get('role', '')} - {exp.get('company', '')} ({exp.get('duration', '')})")
            if exp.get("location"):
                lines.append(f"Location: {exp['location']}")
            for bp in exp.get("bullet_points", []):
                lines.append(f"  * {bp}")
            lines.append("")

    # Projects
    if resume.get("projects"):
        lines.append("PROJECTS")
        lines.append("-" * 30)
        for proj in resume["projects"]:
            header = proj.get("name", "")
            if proj.get("technologies"):
                header += f" [{proj['technologies']}]"
            lines.append(header)
            if proj.get("urls"):
                lines.append(f"Links: {proj['urls']}")
            for bp in proj.get("bullet_points", []):
                lines.append(f"  * {bp}")
            lines.append("")

    # Education
    if resume.get("education"):
        lines.append("EDUCATION")
        lines.append("-" * 30)
        for edu in resume["education"]:
            line = f"{edu.get('degree', '')} in {edu.get('field_of_study', '')} - {edu.get('institution', '')} ({edu.get('year', '')})"
            if edu.get("gpa"):
                line += f" | GPA: {edu['gpa']}"
            lines.append(line)
            if edu.get("highlights"):
                lines.append(f"  * {edu['highlights']}")
            lines.append("")

    # Certifications
    if resume.get("certifications"):
        valid_certs = [c for c in resume["certifications"] if c.get("name")]
        if valid_certs:
            lines.append("CERTIFICATIONS")
            lines.append("-" * 30)
            for cert in valid_certs:
                lines.append(f"  * {cert.get('name')} - {cert.get('organization')} ({cert.get('date')})")
            lines.append("\n")

    # Achievements
    if resume.get("achievements"):
        valid_ach = [a for a in resume["achievements"] if a.strip()]
        if valid_ach:
            lines.append("ACHIEVEMENTS")
            lines.append("-" * 30)
            for ach in valid_ach:
                lines.append(f"  * {ach}")
            lines.append("\n")

    return "\n".join(lines).strip()


def format_resume_markdown(resume: Dict[str, Any]) -> str:
    """Format resume into clean GitHub-flavored markdown."""
    md = []
    p = resume.get("personal_info", {})

    md.append(f"# {p.get('full_name', 'Resume')}")
    if p.get("professional_title"):
        md.append(f"### {p.get('professional_title')}")

    contact = [
        p.get("email"),
        p.get("phone"),
        p.get("location"),
        f"[{p.get('linkedin')}]({p.get('linkedin')})" if p.get("linkedin") else None,
        f"[{p.get('github')}]({p.get('github')})" if p.get("github") else None,
    ]
    md.append(" • ".join([c for c in contact if c]))
    md.append("\n---\n")

    if resume.get("professional_summary"):
        md.append("## Professional Summary\n")
        md.append(resume["professional_summary"] + "\n")

    if resume.get("skills"):
        md.append("## Technical Skills\n")
        for cat, items in resume["skills"].items():
            cat_name = cat.replace("_", " ").title()
            if isinstance(items, list) and items:
                md.append(f"- **{cat_name}:** {', '.join(items)}")
            elif isinstance(items, str) and items:
                md.append(f"- **{cat_name}:** {items}")
        md.append("")

    if resume.get("experience"):
        md.append("## Work Experience\n")
        for exp in resume["experience"]:
            md.append(f"### {exp.get('role')} | {exp.get('company')} *({exp.get('duration', '')})*")
            for bp in exp.get("bullet_points", []):
                md.append(f"- {bp}")
            md.append("")

    if resume.get("projects"):
        md.append("## Technical Projects\n")
        for proj in resume["projects"]:
            tech = f" `{proj.get('technologies')}`" if proj.get("technologies") else ""
            md.append(f"### {proj.get('name')}{tech}")
            if proj.get("urls"):
                md.append(f"*{proj.get('urls')}*")
            for bp in proj.get("bullet_points", []):
                md.append(f"- {bp}")
            md.append("")

    if resume.get("education"):
        md.append("## Education\n")
        for edu in resume["education"]:
            gpa = f" | GPA: {edu.get('gpa')}" if edu.get("gpa") else ""
            md.append(f"**{edu.get('degree')} in {edu.get('field_of_study')}** - {edu.get('institution')} *({edu.get('year')})*{gpa}")
            if edu.get("highlights"):
                md.append(f"- {edu.get('highlights')}")
            md.append("")

    if resume.get("certifications"):
        valid_certs = [c for c in resume["certifications"] if c.get("name")]
        if valid_certs:
            md.append("## Certifications\n")
            for cert in valid_certs:
                md.append(f"- **{cert.get('name')}** - {cert.get('organization')} ({cert.get('date')})")
            md.append("")

    if resume.get("achievements"):
        valid_ach = [a for a in resume["achievements"] if a.strip()]
        if valid_ach:
            md.append("## Achievements\n")
            for ach in valid_ach:
                md.append(f"- {ach}")
            md.append("")

    return "\n".join(md)


def format_resume_html(resume: Dict[str, Any]) -> str:
    """Render resume using the HTML/CSS template."""
    p = resume.get("personal_info", {})
    contact_parts = []
    if p.get("email"):
        contact_parts.append(f'<a href="mailto:{p["email"]}">{html.escape(p["email"])}</a>')
    if p.get("phone"):
        contact_parts.append(html.escape(p["phone"]))
    if p.get("location"):
        contact_parts.append(html.escape(p["location"]))
    if p.get("linkedin"):
        contact_parts.append(f'<a href="{p["linkedin"]}" target="_blank">LinkedIn</a>')
    if p.get("github"):
        contact_parts.append(f'<a href="{p["github"]}" target="_blank">GitHub</a>')
    if p.get("portfolio"):
        contact_parts.append(f'<a href="{p["portfolio"]}" target="_blank">Portfolio</a>')

    contact_line = " • ".join(contact_parts)

    # Format skills HTML
    skills_parts = []
    for cat, items in resume.get("skills", {}).items():
        cat_name = cat.replace("_", " ").title()
        if isinstance(items, list) and items:
            skills_parts.append(f"<p><strong>{html.escape(cat_name)}:</strong> {html.escape(', '.join(items))}</p>")
        elif isinstance(items, str) and items:
            skills_parts.append(f"<p><strong>{html.escape(cat_name)}:</strong> {html.escape(items)}</p>")

    template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "resume_template.html")
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            template_content = f.read()
    else:
        # Fallback inline template
        template_content = "<html><body><h1>{{ personal_info.full_name }}</h1>{{ skills_html }}</body></html>"

    template = Template(template_content)
    return template.render(
        personal_info=p,
        contact_line=contact_line,
        professional_summary=resume.get("professional_summary", ""),
        skills=resume.get("skills"),
        skills_html="".join(skills_parts),
        experience=resume.get("experience", []),
        projects=resume.get("projects", []),
        education=resume.get("education", []),
        certifications=resume.get("certifications", []),
        achievements=resume.get("achievements", []),
    )


def generate_resume_pipeline(
    raw_profile: Dict[str, Any],
    target_job: str = "",
    custom_api_key: Optional[str] = None,
    demo_mode: bool = False,
) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Orchestrate full resume generation pipeline:
    1. Validation
    2. API Call or Mock Generator
    3. Multi-format rendering (HTML, Plain Text, Markdown)
    """
    # 1. Validate
    is_valid, errors = validate_profile(raw_profile)
    if not is_valid:
        return False, None, f"Validation Failed: {'; '.join(errors)}"

    mock_data = get_mock_resume_data(raw_profile)

    # 2. Generation
    if demo_mode:
        resume_data = mock_data
        message = "Generated successfully in Demo/Mock mode (No API charges incurred)."
    else:
        active_key = get_api_key(custom_api_key)
        user_prompt = build_resume_generation_prompt(raw_profile, target_job)
        success, result, msg = call_claude_json(
            system_prompt=RESUME_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            api_key=active_key,
            mock_fallback=mock_data,
        )
        if not success or not result:
            return False, None, msg
        resume_data = result
        message = msg

    # 3. Attach pre-rendered formats
    resume_data["_rendered_text"] = format_resume_text(resume_data)
    resume_data["_rendered_markdown"] = format_resume_markdown(resume_data)
    resume_data["_rendered_html"] = format_resume_html(resume_data)

    return True, resume_data, message

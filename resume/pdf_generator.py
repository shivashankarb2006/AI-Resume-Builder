"""
ReportLab PDF Generator for AI Resume Builder.
Produces high-quality, ATS-optimized, multi-page capable PDFs on A4 paper.
Supports clickable hyperlinks, clean typographical hierarchy, and template themes.
"""
import io
import re
from typing import List, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

from models.resume_schema import ResumeData
from .templates import TEMPLATE_CONFIGS, TEMPLATE_CLASSIC_ATS


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to calculate total pages and draw 'Page X of Y' on multi-page resumes.
    Single-page resumes omit page numbering for clean presentation.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            if num_pages > 1:
                self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#6b7280"))
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(A4[0] - 36, 20, page_text)
        self.restoreState()


def clean_xml_for_pdf(text: str) -> str:
    """Escape XML characters for ReportLab Paragraph formatting."""
    if not text:
        return ""
    # Replace XML entities
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return text


def generate_resume_pdf(resume_data: ResumeData) -> bytes:
    """
    Generate ATS-compliant PDF bytes using ReportLab.
    """
    buffer = io.BytesIO()

    # Retrieve template styling
    template_name = resume_data.selected_template or TEMPLATE_CLASSIC_ATS
    config = TEMPLATE_CONFIGS.get(template_name, TEMPLATE_CONFIGS[TEMPLATE_CLASSIC_ATS])

    font_regular = config["font_family_pdf"]
    font_bold = config["font_family_bold_pdf"]
    heading_color = colors.HexColor(config["heading_color"])
    primary_color = colors.HexColor(config["primary_color"])
    divider_color = colors.HexColor(config["divider_color"])
    accent_hex = config["accent_color"]
    is_center = config["header_alignment"] == "center"

    # Margins: 36pt (0.5 inch)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom Paragraph Styles
    style_name = ParagraphStyle(
        "CandidateName",
        parent=styles["Normal"],
        fontName=font_bold,
        fontSize=20,
        leading=23,
        textColor=heading_color,
        alignment=1 if is_center else 0,
        spaceAfter=3,
    )

    style_contact = ParagraphStyle(
        "ContactBar",
        parent=styles["Normal"],
        fontName=font_regular,
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#4b5563"),
        alignment=1 if is_center else 0,
        spaceAfter=10,
    )

    style_section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName=font_bold,
        fontSize=11,
        leading=13,
        textColor=heading_color,
        spaceBefore=8,
        spaceAfter=2,
        textTransform="uppercase",
    )

    style_subheading_left = ParagraphStyle(
        "SubheadingLeft",
        parent=styles["Normal"],
        fontName=font_bold,
        fontSize=10,
        leading=12,
        textColor=heading_color,
    )

    style_subheading_right = ParagraphStyle(
        "SubheadingRight",
        parent=styles["Normal"],
        fontName=font_regular,
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor("#4b5563"),
        alignment=2,  # Right aligned
    )

    style_body = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName=font_regular,
        fontSize=9.5,
        leading=13,
        textColor=primary_color,
        spaceAfter=3,
    )

    style_bullet = ParagraphStyle(
        "BulletPoint",
        parent=styles["Normal"],
        fontName=font_regular,
        fontSize=9.5,
        leading=13,
        textColor=primary_color,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=2,
    )

    story = []

    # 1. Header (Name + Contact Bar)
    p = resume_data.personal_info
    candidate_name = clean_xml_for_pdf(p.full_name) or "Your Name"
    story.append(Paragraph(candidate_name, style_name))

    contact_parts = []
    if p.email:
        contact_parts.append(f'<a href="mailto:{p.email}" color="{accent_hex}">{clean_xml_for_pdf(p.email)}</a>')
    if p.phone:
        contact_parts.append(clean_xml_for_pdf(p.phone))
    if p.location:
        contact_parts.append(clean_xml_for_pdf(p.location))
    if p.linkedin_url:
        contact_parts.append(f'<a href="{p.linkedin_url}" color="{accent_hex}">LinkedIn</a>')
    if p.github_url:
        contact_parts.append(f'<a href="{p.github_url}" color="{accent_hex}">GitHub</a>')
    if p.portfolio_url:
        contact_parts.append(f'<a href="{p.portfolio_url}" color="{accent_hex}">Portfolio</a>')

    contact_text = " &nbsp;|&nbsp; ".join(contact_parts)
    story.append(Paragraph(contact_text, style_contact))

    enabled = resume_data.enabled_sections
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
            story.append(Paragraph("PROFESSIONAL SUMMARY", style_section_heading))
            story.append(HRFlowable(width="100%", thickness=1, color=divider_color, spaceBefore=1, spaceAfter=4))
            summary_clean = clean_xml_for_pdf(resume_data.summary)
            story.append(Paragraph(summary_clean, style_body))

        elif sec == "Education" and resume_data.education:
            valid_edus = [e for e in resume_data.education if not e.is_empty()]
            if valid_edus:
                story.append(Paragraph("EDUCATION", style_section_heading))
                story.append(HRFlowable(width="100%", thickness=1, color=divider_color, spaceBefore=1, spaceAfter=4))
                for e in valid_edus:
                    inst = clean_xml_for_pdf(e.institution)
                    deg = clean_xml_for_pdf(e.degree)
                    field = clean_xml_for_pdf(e.field_of_study)
                    dates = f"{clean_xml_for_pdf(e.start_year)} – {clean_xml_for_pdf(e.end_year)}" if e.start_year or e.end_year else ""
                    gpa = f" | GPA: {clean_xml_for_pdf(e.gpa)}" if e.gpa else ""

                    header_line = f"<b>{inst}</b>"
                    if dates:
                        header_line += f" <font color='#4b5563'>({dates})</font>"
                    story.append(Paragraph(header_line, style_subheading_left))

                    deg_line = f"{deg} in {field}{gpa}" if field else f"{deg}{gpa}"
                    story.append(Paragraph(deg_line, style_body))

                    if e.relevant_coursework:
                        cw_line = f"<b>Relevant Coursework:</b> {clean_xml_for_pdf(e.relevant_coursework)}"
                        story.append(Paragraph(cw_line, style_bullet))
                    story.append(Spacer(1, 3))

        elif sec == "Skills" and not resume_data.skills.is_empty():
            s = resume_data.skills
            story.append(Paragraph("TECHNICAL SKILLS", style_section_heading))
            story.append(HRFlowable(width="100%", thickness=1, color=divider_color, spaceBefore=1, spaceAfter=4))

            if s.programming_languages:
                story.append(Paragraph(f"<b>Languages:</b> {clean_xml_for_pdf(', '.join(s.programming_languages))}", style_body))
            if s.frameworks:
                story.append(Paragraph(f"<b>Frameworks &amp; Libraries:</b> {clean_xml_for_pdf(', '.join(s.frameworks))}", style_body))
            if s.tools:
                story.append(Paragraph(f"<b>Developer Tools:</b> {clean_xml_for_pdf(', '.join(s.tools))}", style_body))
            if s.ai_ml:
                story.append(Paragraph(f"<b>AI &amp; Machine Learning:</b> {clean_xml_for_pdf(', '.join(s.ai_ml))}", style_body))
            if s.databases:
                story.append(Paragraph(f"<b>Databases:</b> {clean_xml_for_pdf(', '.join(s.databases))}", style_body))
            for c in s.custom_categories:
                if c.category_name.strip() and c.skills:
                    cname = clean_xml_for_pdf(c.category_name)
                    cskills = clean_xml_for_pdf(", ".join(c.skills))
                    story.append(Paragraph(f"<b>{cname}:</b> {cskills}", style_body))

        elif sec == "Experience" and resume_data.experience:
            valid_exps = [e for e in resume_data.experience if not e.is_empty()]
            if valid_exps:
                story.append(Paragraph("PROFESSIONAL EXPERIENCE", style_section_heading))
                story.append(HRFlowable(width="100%", thickness=1, color=divider_color, spaceBefore=1, spaceAfter=4))

                for exp in valid_exps:
                    exp_flowables = []
                    comp = clean_xml_for_pdf(exp.company)
                    role = clean_xml_for_pdf(exp.role)
                    loc = clean_xml_for_pdf(exp.location)
                    end_d = "Present" if exp.is_current else clean_xml_for_pdf(exp.end_date)
                    dates = f"{clean_xml_for_pdf(exp.start_date)} – {end_d}"

                    loc_str = f" — {loc}" if loc else ""
                    exp_flowables.append(Paragraph(f"<b>{comp}</b>{loc_str} &nbsp;|&nbsp; <i>{role}</i> ({dates})", style_subheading_left))

                    bullets = exp.improved_bullets
                    if not bullets and exp.responsibilities:
                        bullets = [b.strip() for b in exp.responsibilities.split("\n") if b.strip()]

                    for b in bullets:
                        bullet_xml = f"&bull;&nbsp; {clean_xml_for_pdf(b)}"
                        exp_flowables.append(Paragraph(bullet_xml, style_bullet))

                    exp_flowables.append(Spacer(1, 4))
                    story.append(KeepTogether(exp_flowables))

        elif sec == "Projects" and resume_data.projects:
            valid_projs = [p for p in resume_data.projects if not p.is_empty()]
            if valid_projs:
                story.append(Paragraph("TECHNICAL PROJECTS", style_section_heading))
                story.append(HRFlowable(width="100%", thickness=1, color=divider_color, spaceBefore=1, spaceAfter=4))

                for proj in valid_projs:
                    proj_flowables = []
                    pname = clean_xml_for_pdf(proj.name)
                    tech = f" | <i>{clean_xml_for_pdf(', '.join(proj.technologies))}</i>" if proj.technologies else ""
                    links = []
                    if proj.github_url:
                        links.append(f'<a href="{proj.github_url}" color="{accent_hex}">GitHub</a>')
                    if proj.demo_url:
                        links.append(f'<a href="{proj.demo_url}" color="{accent_hex}">Live Demo</a>')
                    link_str = f" ({' | '.join(links)})" if links else ""

                    proj_flowables.append(Paragraph(f"<b>{pname}</b>{tech}{link_str}", style_subheading_left))

                    bullets = proj.improved_bullets
                    if not bullets and proj.key_contributions:
                        bullets = [b.strip() for b in proj.key_contributions.split("\n") if b.strip()]
                    elif not bullets and proj.description:
                        bullets = [proj.description]

                    for b in bullets:
                        bullet_xml = f"&bull;&nbsp; {clean_xml_for_pdf(b)}"
                        proj_flowables.append(Paragraph(bullet_xml, style_bullet))

                    proj_flowables.append(Spacer(1, 4))
                    story.append(KeepTogether(proj_flowables))

        elif sec == "Certifications" and resume_data.certifications:
            valid_certs = [c for c in resume_data.certifications if not c.is_empty()]
            if valid_certs:
                story.append(Paragraph("CERTIFICATIONS", style_section_heading))
                story.append(HRFlowable(width="100%", thickness=1, color=divider_color, spaceBefore=1, spaceAfter=4))
                for c in valid_certs:
                    cname = clean_xml_for_pdf(c.name)
                    issuer = f" — {clean_xml_for_pdf(c.issuer)}" if c.issuer else ""
                    date = f" ({clean_xml_for_pdf(c.issue_date)})" if c.issue_date else ""
                    link = f' [<a href="{c.credential_url}" color="{accent_hex}">Verify</a>]' if c.credential_url else ""
                    story.append(Paragraph(f"&bull;&nbsp; <b>{cname}</b>{issuer}{date}{link}", style_bullet))

        elif sec == "Achievements" and resume_data.achievements:
            valid_achs = [a for a in resume_data.achievements if not a.is_empty()]
            if valid_achs:
                story.append(Paragraph("HONORS &amp; ACHIEVEMENTS", style_section_heading))
                story.append(HRFlowable(width="100%", thickness=1, color=divider_color, spaceBefore=1, spaceAfter=4))
                for a in valid_achs:
                    title = clean_xml_for_pdf(a.title)
                    ev = f" | {clean_xml_for_pdf(a.issuer_or_event)}" if a.issuer_or_event else ""
                    dt = f" ({clean_xml_for_pdf(a.date)})" if a.date else ""
                    desc = f": {clean_xml_for_pdf(a.description)}" if a.description else ""
                    story.append(Paragraph(f"&bull;&nbsp; <b>{title}</b>{ev}{dt}{desc}", style_bullet))

        elif sec == "Volunteer Experience" and resume_data.volunteer:
            valid_vols = [v for v in resume_data.volunteer if not v.is_empty()]
            if valid_vols:
                story.append(Paragraph("VOLUNTEER &amp; LEADERSHIP", style_section_heading))
                story.append(HRFlowable(width="100%", thickness=1, color=divider_color, spaceBefore=1, spaceAfter=4))
                for v in valid_vols:
                    org = clean_xml_for_pdf(v.organization)
                    vrole = clean_xml_for_pdf(v.role)
                    vdates = f" ({clean_xml_for_pdf(v.dates)})" if v.dates else ""
                    vdetails = f": {clean_xml_for_pdf(v.details)}" if v.details else ""
                    story.append(Paragraph(f"&bull;&nbsp; <b>{vrole}</b> at {org}{vdates}{vdetails}", style_bullet))

    doc.build(story, canvasmaker=NumberedCanvas)
    return buffer.getvalue()

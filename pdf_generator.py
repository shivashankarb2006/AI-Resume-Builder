from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable
)


SECTION_NAMES = {
    "PROFESSIONAL SUMMARY",
    "SUMMARY",
    "CAREER OBJECTIVE",
    "EDUCATION",
    "TECHNICAL SKILLS",
    "SKILLS",
    "PROJECTS",
    "EXPERIENCE",
    "WORK EXPERIENCE",
    "INTERNSHIPS",
    "CERTIFICATIONS",
    "ACHIEVEMENTS",
    "LANGUAGES",
}


def create_pdf(resume_text, template="Classic ATS"):

    file_path = "AI_Resume.pdf"

    # =====================================================
    # PAGE SETTINGS
    # =====================================================

    if template == "Minimal Student":

        margins = {
            "rightMargin": 14 * mm,
            "leftMargin": 14 * mm,
            "topMargin": 12 * mm,
            "bottomMargin": 12 * mm
        }

    elif template == "Modern Professional":

        margins = {
            "rightMargin": 18 * mm,
            "leftMargin": 18 * mm,
            "topMargin": 16 * mm,
            "bottomMargin": 16 * mm
        }

    else:

        margins = {
            "rightMargin": 18 * mm,
            "leftMargin": 18 * mm,
            "topMargin": 15 * mm,
            "bottomMargin": 15 * mm
        }

    document = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        **margins
    )

    # =====================================================
    # STYLES
    # =====================================================

    if template == "Modern Professional":

        name_style = ParagraphStyle(
            "Name",
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=23,
            alignment=TA_CENTER,
            spaceAfter=5
        )

        heading_style = ParagraphStyle(
            "Heading",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            spaceBefore=9,
            spaceAfter=4
        )

        body_size = 10

    elif template == "Minimal Student":

        name_style = ParagraphStyle(
            "Name",
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=19,
            alignment=TA_CENTER,
            spaceAfter=4
        )

        heading_style = ParagraphStyle(
            "Heading",
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=12,
            spaceBefore=5,
            spaceAfter=2
        )

        body_size = 9

    else:

        name_style = ParagraphStyle(
            "Name",
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            spaceAfter=5
        )

        heading_style = ParagraphStyle(
            "Heading",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            spaceBefore=8,
            spaceAfter=4
        )

        body_size = 9.5

    contact_style = ParagraphStyle(
        "Contact",
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        spaceAfter=7
    )

    body_style = ParagraphStyle(
        "Body",
        fontName="Helvetica",
        fontSize=body_size,
        leading=13,
        spaceAfter=3
    )

    bullet_style = ParagraphStyle(
        "Bullet",
        fontName="Helvetica",
        fontSize=body_size,
        leading=13,
        leftIndent=10,
        firstLineIndent=-6,
        spaceAfter=2
    )

    story = []

    lines = resume_text.split("\n")

    first_line = True

    # =====================================================
    # PROCESS RESUME
    # =====================================================

    for raw_line in lines:

        line = raw_line.strip()

        if not line:
            continue

        # =================================================
        # NAME
        # =================================================

        if first_line:

            story.append(
                Paragraph(
                    line,
                    name_style
                )
            )

            first_line = False

            continue

        # =================================================
        # SECTION HEADINGS
        # =================================================

        if line.upper() in SECTION_NAMES:

            story.append(
                Paragraph(
                    line.upper(),
                    heading_style
                )
            )

            story.append(
                HRFlowable(
                    width="100%",
                    thickness=0.5,
                    spaceAfter=4
                )
            )

            continue

        # =================================================
        # CONTACT
        # =================================================

        if (
            "@" in line
            or "linkedin.com" in line.lower()
            or "github.com" in line.lower()
            or line.startswith("+91")
        ):

            story.append(
                Paragraph(
                    line,
                    contact_style
                )
            )

            continue

        # =================================================
        # BULLET
        # =================================================

        if line.startswith("-") or line.startswith("•"):

            clean_line = line.lstrip("-•").strip()

            clean_line = (
                clean_line
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )

            story.append(
                Paragraph(
                    "• " + clean_line,
                    bullet_style
                )
            )

            continue

        # =================================================
        # NORMAL TEXT
        # =================================================

        safe_line = (
            line
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

        story.append(
            Paragraph(
                safe_line,
                body_style
            )
        )

    document.build(story)

    return file_path
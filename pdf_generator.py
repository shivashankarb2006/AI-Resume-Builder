from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    Table,
    TableStyle,
    KeepTogether
)
from reportlab.lib import colors


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


def escape_text(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def create_pdf(resume_text, template="Classic ATS"):

    file_path = "AI_Resume.pdf"

    # =====================================================
    # TEMPLATE SETTINGS
    # =====================================================

    if template == "Modern Professional":

        document = SimpleDocTemplate(
            file_path,
            pagesize=A4,
            rightMargin=16 * mm,
            leftMargin=16 * mm,
            topMargin=14 * mm,
            bottomMargin=14 * mm
        )

        name_style = ParagraphStyle(
            "ModernName",
            fontName="Helvetica-Bold",
            fontSize=23,
            leading=27,
            alignment=TA_LEFT,
            spaceAfter=3
        )

        contact_style = ParagraphStyle(
            "ModernContact",
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            alignment=TA_LEFT,
            spaceAfter=8
        )

        heading_style = ParagraphStyle(
            "ModernHeading",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#1F4E79"),
            spaceBefore=9,
            spaceAfter=4
        )

        body_style = ParagraphStyle(
            "ModernBody",
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            spaceAfter=3
        )

        bullet_style = ParagraphStyle(
            "ModernBullet",
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            leftIndent=12,
            firstLineIndent=-7,
            spaceAfter=2
        )

    elif template == "Minimal Student":

        document = SimpleDocTemplate(
            file_path,
            pagesize=A4,
            rightMargin=13 * mm,
            leftMargin=13 * mm,
            topMargin=11 * mm,
            bottomMargin=11 * mm
        )

        name_style = ParagraphStyle(
            "MinimalName",
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=21,
            alignment=TA_CENTER,
            spaceAfter=2
        )

        contact_style = ParagraphStyle(
            "MinimalContact",
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            alignment=TA_CENTER,
            spaceAfter=5
        )

        heading_style = ParagraphStyle(
            "MinimalHeading",
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=12,
            textColor=colors.black,
            spaceBefore=5,
            spaceAfter=2
        )

        body_style = ParagraphStyle(
            "MinimalBody",
            fontName="Helvetica",
            fontSize=8.7,
            leading=11,
            spaceAfter=2
        )

        bullet_style = ParagraphStyle(
            "MinimalBullet",
            fontName="Helvetica",
            fontSize=8.7,
            leading=11,
            leftIndent=10,
            firstLineIndent=-6,
            spaceAfter=1
        )

    else:

        # CLASSIC ATS

        document = SimpleDocTemplate(
            file_path,
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm
        )

        name_style = ParagraphStyle(
            "ClassicName",
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=23,
            alignment=TA_CENTER,
            spaceAfter=3
        )

        contact_style = ParagraphStyle(
            "ClassicContact",
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
            spaceAfter=7
        )

        heading_style = ParagraphStyle(
            "ClassicHeading",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.black,
            spaceBefore=8,
            spaceAfter=4
        )

        body_style = ParagraphStyle(
            "ClassicBody",
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            spaceAfter=3
        )

        bullet_style = ParagraphStyle(
            "ClassicBullet",
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            leftIndent=11,
            firstLineIndent=-6,
            spaceAfter=2
        )

    story = []

    lines = resume_text.split("\n")

    first_line = True

    # =====================================================
    # HEADER
    # =====================================================

    if lines:

        name = lines[0].strip()

        if name:

            story.append(
                Paragraph(
                    escape_text(name),
                    name_style
                )
            )

            first_line = False

    # =====================================================
    # PROCESS RESUME
    # =====================================================

    for raw_line in lines[1:]:

        line = raw_line.strip()

        if not line:
            continue

        # -------------------------------------------------
        # CONTACT
        # -------------------------------------------------

        if (
            "@" in line
            or "linkedin.com" in line.lower()
            or "github.com" in line.lower()
            or line.startswith("+91")
        ):

            story.append(
                Paragraph(
                    escape_text(line),
                    contact_style
                )
            )

            continue

        # -------------------------------------------------
        # SECTION HEADINGS
        # -------------------------------------------------

        if line.upper() in SECTION_NAMES:

            heading = Paragraph(
                escape_text(line.upper()),
                heading_style
            )

            if template == "Modern Professional":

                line_element = HRFlowable(
                    width="100%",
                    thickness=1.2,
                    color=colors.HexColor("#1F4E79"),
                    spaceBefore=1,
                    spaceAfter=5
                )

                story.append(
                    KeepTogether([
                        heading,
                        line_element
                    ])
                )

            elif template == "Minimal Student":

                line_element = HRFlowable(
                    width="100%",
                    thickness=0.5,
                    color=colors.black,
                    spaceBefore=1,
                    spaceAfter=3
                )

                story.append(
                    KeepTogether([
                        heading,
                        line_element
                    ])
                )

            else:

                line_element = HRFlowable(
                    width="100%",
                    thickness=0.7,
                    color=colors.black,
                    spaceBefore=1,
                    spaceAfter=4
                )

                story.append(
                    KeepTogether([
                        heading,
                        line_element
                    ])
                )

            continue

        # -------------------------------------------------
        # BULLETS
        # -------------------------------------------------

        if line.startswith("-") or line.startswith("•"):

            clean_line = line.lstrip("-•").strip()

            story.append(
                Paragraph(
                    "• " + escape_text(clean_line),
                    bullet_style
                )
            )

            continue

        # -------------------------------------------------
        # NORMAL TEXT
        # -------------------------------------------------

        story.append(
            Paragraph(
                escape_text(line),
                body_style
            )
        )

    # =====================================================
    # BUILD PDF
    # =====================================================

    document.build(story)

    return file_path
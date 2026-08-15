from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    Table,
    TableStyle
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


def clean_text(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def create_pdf(resume_text, template="Classic ATS"):

    file_path = f"AI_Resume_{template.replace(' ', '_')}.pdf"

    # =====================================================
    # CLASSIC ATS
    # =====================================================

    if template == "Classic ATS":

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
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            spaceAfter=4
        )

        contact_style = ParagraphStyle(
            "ClassicContact",
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
            spaceAfter=8
        )

        heading_style = ParagraphStyle(
            "ClassicHeading",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            spaceBefore=8,
            spaceAfter=3
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
            leftIndent=10,
            firstLineIndent=-6,
            spaceAfter=2
        )

        story = []
        lines = resume_text.split("\n")
        first_line = True

        for raw_line in lines:

            line = raw_line.strip()

            if not line:
                continue

            if first_line:

                story.append(
                    Paragraph(
                        clean_text(line),
                        name_style
                    )
                )

                first_line = False
                continue

            if (
                "@" in line
                or "linkedin.com" in line.lower()
                or "github.com" in line.lower()
                or line.startswith("+91")
            ):

                story.append(
                    Paragraph(
                        clean_text(line),
                        contact_style
                    )
                )

                continue

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
                        thickness=0.7,
                        spaceAfter=4
                    )
                )

                continue

            if line.startswith("-") or line.startswith("•"):

                clean_line = line.lstrip("-•").strip()

                story.append(
                    Paragraph(
                        "• " + clean_text(clean_line),
                        bullet_style
                    )
                )

                continue

            story.append(
                Paragraph(
                    clean_text(line),
                    body_style
                )
            )

        document.build(story)

        return file_path


    # =====================================================
    # MODERN PROFESSIONAL
    # =====================================================

    elif template == "Modern Professional":

        document = SimpleDocTemplate(
            file_path,
            pagesize=A4,
            rightMargin=15 * mm,
            leftMargin=15 * mm,
            topMargin=14 * mm,
            bottomMargin=14 * mm
        )

        name_style = ParagraphStyle(
            "ModernName",
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=25,
            alignment=TA_LEFT,
            spaceAfter=3
        )

        contact_style = ParagraphStyle(
            "ModernContact",
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            alignment=TA_LEFT,
            spaceAfter=8
        )

        heading_style = ParagraphStyle(
            "ModernHeading",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#1F4E79"),
            spaceBefore=8,
            spaceAfter=3
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
            leftIndent=10,
            firstLineIndent=-6,
            spaceAfter=2
        )

        story = []

        lines = resume_text.split("\n")
        first_line = True

        # Modern header
        for raw_line in lines:

            line = raw_line.strip()

            if not line:
                continue

            if first_line:

                story.append(
                    Paragraph(
                        clean_text(line),
                        name_style
                    )
                )

                story.append(
                    HRFlowable(
                        width="100%",
                        thickness=1.5,
                        color=colors.HexColor("#1F4E79"),
                        spaceAfter=5
                    )
                )

                first_line = False
                continue

            if (
                "@" in line
                or "linkedin.com" in line.lower()
                or "github.com" in line.lower()
                or line.startswith("+91")
            ):

                story.append(
                    Paragraph(
                        clean_text(line),
                        contact_style
                    )
                )

                continue

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
                        color=colors.HexColor("#B7C9D6"),
                        spaceAfter=4
                    )
                )

                continue

            if line.startswith("-") or line.startswith("•"):

                clean_line = line.lstrip("-•").strip()

                story.append(
                    Paragraph(
                        "• " + clean_text(clean_line),
                        bullet_style
                    )
                )

                continue

            story.append(
                Paragraph(
                    clean_text(line),
                    body_style
                )
            )

        document.build(story)

        return file_path


    # =====================================================
    # MINIMAL STUDENT
    # =====================================================

    else:

        document = SimpleDocTemplate(
            file_path,
            pagesize=A4,
            rightMargin=14 * mm,
            leftMargin=14 * mm,
            topMargin=12 * mm,
            bottomMargin=12 * mm
        )

        name_style = ParagraphStyle(
            "MinimalName",
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=19,
            alignment=TA_CENTER,
            spaceAfter=3
        )

        contact_style = ParagraphStyle(
            "MinimalContact",
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            alignment=TA_CENTER,
            spaceAfter=6
        )

        heading_style = ParagraphStyle(
            "MinimalHeading",
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=12,
            spaceBefore=6,
            spaceAfter=2
        )

        body_style = ParagraphStyle(
            "MinimalBody",
            fontName="Helvetica",
            fontSize=9,
            leading=11.5,
            spaceAfter=2
        )

        bullet_style = ParagraphStyle(
            "MinimalBullet",
            fontName="Helvetica",
            fontSize=9,
            leading=11.5,
            leftIndent=9,
            firstLineIndent=-5,
            spaceAfter=1
        )

        story = []

        lines = resume_text.split("\n")
        first_line = True

        for raw_line in lines:

            line = raw_line.strip()

            if not line:
                continue

            if first_line:

                story.append(
                    Paragraph(
                        clean_text(line),
                        name_style
                    )
                )

                first_line = False
                continue

            if (
                "@" in line
                or "linkedin.com" in line.lower()
                or "github.com" in line.lower()
                or line.startswith("+91")
            ):

                story.append(
                    Paragraph(
                        clean_text(line),
                        contact_style
                    )
                )

                continue

            if line.upper() in SECTION_NAMES:

                story.append(
                    Spacer(
                        1,
                        2
                    )
                )

                story.append(
                    Paragraph(
                        line.upper(),
                        heading_style
                    )
                )

                continue

            if line.startswith("-") or line.startswith("•"):

                clean_line = line.lstrip("-•").strip()

                story.append(
                    Paragraph(
                        "• " + clean_text(clean_line),
                        bullet_style
                    )
                )

                continue

            story.append(
                Paragraph(
                    clean_text(line),
                    body_style
                )
            )

        document.build(story)

        return file_path
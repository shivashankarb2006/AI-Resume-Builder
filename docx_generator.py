from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


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


def add_bottom_border(paragraph):
    """Add a simple line below a paragraph."""

    p = paragraph._p
    pPr = p.get_or_add_pPr()

    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")

    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "1")

    pBdr.append(bottom)
    pPr.append(pBdr)


def create_docx(resume_text, template="Classic ATS"):

    document = Document()

    # =====================================================
    # PAGE SETTINGS
    # =====================================================

    section = document.sections[0]

    if template == "Minimal Student":

        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)
        section.left_margin = Inches(0.6)
        section.right_margin = Inches(0.6)

    elif template == "Modern Professional":

        section.top_margin = Inches(0.65)
        section.bottom_margin = Inches(0.65)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    else:

        section.top_margin = Inches(0.6)
        section.bottom_margin = Inches(0.6)
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)

    # =====================================================
    # DEFAULT FONT
    # =====================================================

    normal_style = document.styles["Normal"]

    if template == "Modern Professional":
        normal_style.font.name = "Calibri"
        normal_style.font.size = Pt(10)

    elif template == "Minimal Student":
        normal_style.font.name = "Arial"
        normal_style.font.size = Pt(9.5)

    else:
        normal_style.font.name = "Arial"
        normal_style.font.size = Pt(10)

    # =====================================================
    # RESUME CONTENT
    # =====================================================

    lines = resume_text.split("\n")

    first_line = True

    for raw_line in lines:

        line = raw_line.strip()

        if not line:
            continue

        # =================================================
        # NAME
        # =================================================

        if first_line:

            paragraph = document.add_paragraph()

            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

            if template == "Modern Professional":

                run = paragraph.add_run(line)
                run.bold = True
                run.font.name = "Calibri"
                run.font.size = Pt(20)

            elif template == "Minimal Student":

                run = paragraph.add_run(line)
                run.bold = True
                run.font.name = "Arial"
                run.font.size = Pt(16)

            else:

                run = paragraph.add_run(line)
                run.bold = True
                run.font.name = "Arial"
                run.font.size = Pt(18)

            first_line = False

            continue

        # =================================================
        # SECTION HEADINGS
        # =================================================

        if line.upper() in SECTION_NAMES:

            paragraph = document.add_paragraph()

            if template == "Minimal Student":

                paragraph.paragraph_format.space_before = Pt(5)
                paragraph.paragraph_format.space_after = Pt(2)

            elif template == "Modern Professional":

                paragraph.paragraph_format.space_before = Pt(9)
                paragraph.paragraph_format.space_after = Pt(3)

            else:

                paragraph.paragraph_format.space_before = Pt(8)
                paragraph.paragraph_format.space_after = Pt(3)

            run = paragraph.add_run(line.upper())

            run.bold = True

            if template == "Modern Professional":

                run.font.name = "Calibri"
                run.font.size = Pt(11)

            elif template == "Minimal Student":

                run.font.name = "Arial"
                run.font.size = Pt(10)

            else:

                run.font.name = "Arial"
                run.font.size = Pt(11)

            add_bottom_border(paragraph)

            continue

        # =================================================
        # CONTACT INFORMATION
        # =================================================

        if (
            "@" in line
            or "linkedin.com" in line.lower()
            or "github.com" in line.lower()
            or line.startswith("+91")
        ):

            paragraph = document.add_paragraph()

            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

            run = paragraph.add_run(line)

            run.font.size = Pt(9)

            continue

        # =================================================
        # BULLET POINTS
        # =================================================

        if line.startswith("-") or line.startswith("•"):

            clean_line = line.lstrip("-•").strip()

            paragraph = document.add_paragraph(
                style="List Bullet"
            )

            paragraph.paragraph_format.space_after = Pt(2)

            run = paragraph.add_run(clean_line)

            run.font.size = (
                Pt(9.5)
                if template == "Minimal Student"
                else Pt(10)
            )

            continue

        # =================================================
        # NORMAL CONTENT
        # =================================================

        paragraph = document.add_paragraph()

        paragraph.paragraph_format.space_after = Pt(3)

        run = paragraph.add_run(line)

        if template == "Minimal Student":

            run.font.name = "Arial"
            run.font.size = Pt(9.5)

        elif template == "Modern Professional":

            run.font.name = "Calibri"
            run.font.size = Pt(10)

        else:

            run.font.name = "Arial"
            run.font.size = Pt(10)

    # =====================================================
    # SAVE
    # =====================================================

    file_path = "AI_Resume.docx"

    document.save(file_path)

    return file_path
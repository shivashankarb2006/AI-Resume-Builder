from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
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


def set_cell_shading(cell, fill):
    """Set background color of a table cell."""

    tc_pr = cell._tc.get_or_add_tcPr()

    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)

    tc_pr.append(shd)


def remove_table_borders(table):
    """Remove table borders."""

    tbl = table._tbl
    tbl_pr = tbl.tblPr

    borders = OxmlElement("w:tblBorders")

    for edge in (
        "top",
        "left",
        "bottom",
        "right",
        "insideH",
        "insideV"
    ):

        element = OxmlElement(f"w:{edge}")
        element.set(qn("w:val"), "nil")
        borders.append(element)

    tbl_pr.append(borders)


def add_bottom_border(paragraph, color="000000"):
    """Add a line below a paragraph."""

    p = paragraph._p
    pPr = p.get_or_add_pPr()

    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")

    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "2")
    bottom.set(qn("w:color"), color)

    pBdr.append(bottom)
    pPr.append(pBdr)


def add_section_heading(
    document,
    text,
    template
):

    paragraph = document.add_paragraph()

    if template == "Modern Professional":

        paragraph.paragraph_format.space_before = Pt(9)
        paragraph.paragraph_format.space_after = Pt(3)

        run = paragraph.add_run(text.upper())

        run.bold = True
        run.font.name = "Calibri"
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(
            31,
            78,
            121
        )

        add_bottom_border(
            paragraph,
            "B7C9D6"
        )

    elif template == "Minimal Student":

        paragraph.paragraph_format.space_before = Pt(5)
        paragraph.paragraph_format.space_after = Pt(2)

        run = paragraph.add_run(text.upper())

        run.bold = True
        run.font.name = "Arial"
        run.font.size = Pt(10)

    else:

        paragraph.paragraph_format.space_before = Pt(8)
        paragraph.paragraph_format.space_after = Pt(3)

        run = paragraph.add_run(text.upper())

        run.bold = True
        run.font.name = "Arial"
        run.font.size = Pt(11)

        add_bottom_border(
            paragraph
        )

    return paragraph


def add_content(
    document,
    line,
    template
):

    if line.startswith("-") or line.startswith("•"):

        clean_line = line.lstrip("-•").strip()

        paragraph = document.add_paragraph(
            style="List Bullet"
        )

        paragraph.paragraph_format.space_after = Pt(
            1 if template == "Minimal Student" else 2
        )

        run = paragraph.add_run(
            clean_line
        )

    else:

        paragraph = document.add_paragraph()

        paragraph.paragraph_format.space_after = Pt(
            2 if template == "Minimal Student" else 3
        )

        run = paragraph.add_run(
            line
        )

    if template == "Modern Professional":

        run.font.name = "Calibri"
        run.font.size = Pt(10)

    elif template == "Minimal Student":

        run.font.name = "Arial"
        run.font.size = Pt(9.5)

    else:

        run.font.name = "Arial"
        run.font.size = Pt(10)

    return paragraph


def create_docx(
    resume_text,
    template="Classic ATS"
):

    file_path = (
        f"AI_Resume_"
        f"{template.replace(' ', '_')}.docx"
    )

    document = Document()

    section = document.sections[0]

    # =====================================================
    # PAGE SETTINGS
    # =====================================================

    if template == "Modern Professional":

        section.top_margin = Inches(0.55)
        section.bottom_margin = Inches(0.55)
        section.left_margin = Inches(0.65)
        section.right_margin = Inches(0.65)

    elif template == "Minimal Student":

        section.top_margin = Inches(0.45)
        section.bottom_margin = Inches(0.45)
        section.left_margin = Inches(0.55)
        section.right_margin = Inches(0.55)

    else:

        section.top_margin = Inches(0.6)
        section.bottom_margin = Inches(0.6)
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)

    # =====================================================
    # NORMAL STYLE
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
    # READ RESUME
    # =====================================================

    lines = [
        line.strip()
        for line in resume_text.split("\n")
        if line.strip()
    ]

    if not lines:
        document.save(file_path)
        return file_path

    name = lines[0]

    remaining_lines = lines[1:]

    # =====================================================
    # MODERN PROFESSIONAL HEADER
    # =====================================================

    if template == "Modern Professional":

        header_table = document.add_table(
            rows=1,
            cols=1
        )

        header_table.alignment = (
            WD_TABLE_ALIGNMENT.CENTER
        )

        remove_table_borders(
            header_table
        )

        cell = header_table.cell(0, 0)

        set_cell_shading(
            cell,
            "EAF1F8"
        )

        cell.vertical_alignment = (
            WD_CELL_VERTICAL_ALIGNMENT.CENTER
        )

        paragraph = cell.paragraphs[0]

        paragraph.alignment = (
            WD_ALIGN_PARAGRAPH.LEFT
        )

        paragraph.paragraph_format.space_after = Pt(2)

        run = paragraph.add_run(name)

        run.bold = True
        run.font.name = "Calibri"
        run.font.size = Pt(22)
        run.font.color.rgb = RGBColor(
            31,
            78,
            121
        )

        # Add contact information
        contact_lines = []

        for line in remaining_lines:

            if (
                "@" in line
                or "linkedin.com" in line.lower()
                or "github.com" in line.lower()
                or line.startswith("+91")
            ):

                contact_lines.append(line)

        if contact_lines:

            paragraph = cell.add_paragraph()

            paragraph.paragraph_format.space_after = Pt(3)

            run = paragraph.add_run(
                "  |  ".join(contact_lines)
            )

            run.font.name = "Calibri"
            run.font.size = Pt(9)

        document.add_paragraph()

    # =====================================================
    # MINIMAL STUDENT HEADER
    # =====================================================

    elif template == "Minimal Student":

        paragraph = document.add_paragraph()

        paragraph.alignment = (
            WD_ALIGN_PARAGRAPH.CENTER
        )

        paragraph.paragraph_format.space_after = Pt(2)

        run = paragraph.add_run(name)

        run.bold = True
        run.font.name = "Arial"
        run.font.size = Pt(16)

        contact_lines = []

        for line in remaining_lines:

            if (
                "@" in line
                or "linkedin.com" in line.lower()
                or "github.com" in line.lower()
                or line.startswith("+91")
            ):

                contact_lines.append(line)

        if contact_lines:

            paragraph = document.add_paragraph()

            paragraph.alignment = (
                WD_ALIGN_PARAGRAPH.CENTER
            )

            paragraph.paragraph_format.space_after = Pt(5)

            run = paragraph.add_run(
                " | ".join(contact_lines)
            )

            run.font.name = "Arial"
            run.font.size = Pt(8.5)

    # =====================================================
    # CLASSIC ATS HEADER
    # =====================================================

    else:

        paragraph = document.add_paragraph()

        paragraph.alignment = (
            WD_ALIGN_PARAGRAPH.CENTER
        )

        paragraph.paragraph_format.space_after = Pt(3)

        run = paragraph.add_run(name)

        run.bold = True
        run.font.name = "Arial"
        run.font.size = Pt(18)

        contact_lines = []

        for line in remaining_lines:

            if (
                "@" in line
                or "linkedin.com" in line.lower()
                or "github.com" in line.lower()
                or line.startswith("+91")
            ):

                contact_lines.append(line)

        if contact_lines:

            paragraph = document.add_paragraph()

            paragraph.alignment = (
                WD_ALIGN_PARAGRAPH.CENTER
            )

            paragraph.paragraph_format.space_after = Pt(6)

            run = paragraph.add_run(
                " | ".join(contact_lines)
            )

            run.font.name = "Arial"
            run.font.size = Pt(9)

    # =====================================================
    # CONTENT
    # =====================================================

    for line in remaining_lines:

        # Skip contact lines already placed in header
        if (
            "@" in line
            or "linkedin.com" in line.lower()
            or "github.com" in line.lower()
            or line.startswith("+91")
        ):

            continue

        # Section heading
        if line.upper() in SECTION_NAMES:

            add_section_heading(
                document,
                line,
                template
            )

            continue

        # Normal content
        add_content(
            document,
            line,
            template
        )

    # =====================================================
    # MODERN FOOTER
    # =====================================================

    if template == "Modern Professional":

        footer = section.footer

        paragraph = footer.paragraphs[0]

        paragraph.alignment = (
            WD_ALIGN_PARAGRAPH.CENTER
        )

        run = paragraph.add_run(
            "Professional Resume"
        )

        run.font.name = "Calibri"
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor(
            100,
            100,
            100
        )

    # =====================================================
    # SAVE
    # =====================================================

    document.save(file_path)

    return file_path
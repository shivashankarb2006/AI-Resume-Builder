"""
Resume Template Specifications and Configurations.
Defines typography, color palettes, and structural layouts for:
1. Classic ATS (Maximum compatibility, traditional serif/clean styling)
2. Modern Professional (Clean visual hierarchy, subtle slate/navy accents)
3. Technical Specialist (Engineering/IT focused, skills prioritized near top)
"""
from typing import Dict, Any

TEMPLATE_CLASSIC_ATS = "Classic ATS"
TEMPLATE_MODERN_PROFESSIONAL = "Modern Professional"
TEMPLATE_TECHNICAL_SPECIALIST = "Technical Specialist"

RESUME_TEMPLATES = [
    TEMPLATE_CLASSIC_ATS,
    TEMPLATE_MODERN_PROFESSIONAL,
    TEMPLATE_TECHNICAL_SPECIALIST,
]

TEMPLATE_CONFIGS: Dict[str, Dict[str, Any]] = {
    TEMPLATE_CLASSIC_ATS: {
        "name": "Classic ATS",
        "description": "Timeless single-column layout with traditional typography. Guaranteed highest ATS parse rates.",
        "font_family_pdf": "Times-Roman",
        "font_family_bold_pdf": "Times-Bold",
        "font_family_docx": "Times New Roman",
        "font_family_html": "'Georgia', 'Times New Roman', serif",
        "primary_color": "#111827",      # Deep near-black
        "heading_color": "#000000",      # Pure black
        "accent_color": "#374151",       # Charcoal gray
        "divider_color": "#4b5563",      # Medium gray divider line
        "header_alignment": "center",
        "section_order": [
            "Professional Summary",
            "Education",
            "Skills",
            "Experience",
            "Projects",
            "Certifications",
            "Achievements",
            "Relevant Coursework",
            "Volunteer Experience",
        ],
    },
    TEMPLATE_MODERN_PROFESSIONAL: {
        "name": "Modern Professional",
        "description": "Clean, contemporary visual hierarchy with subtle slate/navy accents. Fully ATS-compliant.",
        "font_family_pdf": "Helvetica",
        "font_family_bold_pdf": "Helvetica-Bold",
        "font_family_docx": "Calibri",
        "font_family_html": "'Segoe UI', -apple-system, Roboto, sans-serif",
        "primary_color": "#1e293b",      # Slate 800
        "heading_color": "#0f172a",      # Slate 900
        "accent_color": "#2563eb",       # Royal blue accent
        "divider_color": "#cbd5e1",      # Light slate divider line
        "header_alignment": "left",
        "section_order": [
            "Professional Summary",
            "Experience",
            "Projects",
            "Education",
            "Skills",
            "Certifications",
            "Achievements",
            "Relevant Coursework",
            "Volunteer Experience",
        ],
    },
    TEMPLATE_TECHNICAL_SPECIALIST: {
        "name": "Technical Specialist",
        "description": "Tailored for Software Engineers, IT, and AI/ML candidates. Skills and technical projects prioritized.",
        "font_family_pdf": "Helvetica",
        "font_family_bold_pdf": "Helvetica-Bold",
        "font_family_docx": "Arial",
        "font_family_html": "'Inter', 'Roboto', 'Segoe UI', sans-serif",
        "primary_color": "#0f172a",      # Midnight navy
        "heading_color": "#0369a1",      # Deep cyan
        "accent_color": "#0284c7",       # Sky blue
        "divider_color": "#bae6fd",      # Soft blue divider
        "header_alignment": "left",
        "section_order": [
            "Professional Summary",
            "Skills",
            "Projects",
            "Experience",
            "Education",
            "Certifications",
            "Achievements",
            "Relevant Coursework",
            "Volunteer Experience",
        ],
    },
}

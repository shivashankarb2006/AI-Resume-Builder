"""
General helper functions for AI Resume Builder.
Includes filename sanitization, bullet point normalization, and HTML escaping.
"""
import html
import re
from typing import List


def generate_resume_filename(name: str, extension: str = "pdf") -> str:
    """
    Generate a clean, sanitized filename from candidate name.
    Example: 'Alex Chen' -> 'Alex_Chen_Resume.pdf'
    Fallback if empty: 'Resume.pdf'
    """
    ext = extension.lstrip(".").lower()
    if not name or not name.strip():
        return f"Resume.{ext}"

    # Replace spaces and punctuation with underscores, keep alphanumeric
    clean_name = re.sub(r"[^a-zA-Z0-9\s_-]", "", name.strip())
    clean_name = re.sub(r"[\s_]+", "_", clean_name)

    if not clean_name:
        return f"Resume.{ext}"

    return f"{clean_name}_Resume.{ext}"


def split_lines_or_commas(raw_text: str) -> List[str]:
    """
    Parse a comma-separated or newline-separated string into a list of non-empty items.
    """
    if not raw_text:
        return []
    # Replace newlines with commas, then split
    normalized = raw_text.replace("\n", ",")
    items = [item.strip() for item in normalized.split(",") if item.strip()]
    return items


def format_bullet_point(bullet: str) -> str:
    """
    Normalize bullet point text: strip leading dashes/bullets, capitalize, ensure clean period.
    """
    if not bullet:
        return ""
    # Strip leading bullet symbols like -, *, •, 1., etc.
    cleaned = re.sub(r"^[\s*•\-–—\d\.\)]+", "", bullet).strip()
    if not cleaned:
        return ""
    # Capitalize first letter
    cleaned = cleaned[0].upper() + cleaned[1:]
    # Ensure ends with a period if not ending with punctuation
    if cleaned[-1] not in ".!?":
        cleaned += "."
    return cleaned


def sanitize_html(text: str) -> str:
    """Escape HTML characters to prevent XSS when rendering into HTML preview."""
    if not text:
        return ""
    return html.escape(str(text))

"""
AI Resume Builder - Input Validation & Sanitization Module
"""

import re
from typing import Tuple, List, Dict, Any

# Standard RFC 5322 compliant regex for basic email validation
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

# Robust URL regex (supports http, https, or bare www/domain)
URL_REGEX = re.compile(
    r"^(https?:\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$"
)


def validate_email(email: str) -> bool:
    """Validate email address format. Returns True if valid or empty (optional)."""
    if not email or not email.strip():
        return True  # Handled separately if email is required
    return bool(EMAIL_REGEX.match(email.strip()))


def validate_url(url: str) -> bool:
    """Validate web URL format. Returns True if valid or empty (optional)."""
    if not url or not url.strip():
        return True
    return bool(URL_REGEX.match(url.strip()))


def sanitize_text(text: str) -> str:
    """Clean up unnecessary trailing whitespace and null bytes."""
    if not text:
        return ""
    # Strip null characters and whitespace
    return text.replace("\x00", "").strip()


def validate_profile(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate full resume data dictionary before processing.
    Returns (is_valid, list_of_error_messages).
    """
    errors: List[str] = []
    personal = data.get("personal_info", {})

    # 1. Required Personal Info checks
    if not personal.get("full_name", "").strip():
        errors.append("Full Name is required.")

    email = personal.get("email", "").strip()
    if not email:
        errors.append("Email address is required.")
    elif not validate_email(email):
        errors.append(f"'{email}' is not a valid email address.")

    # 2. URL Validations
    for field, label in [
        ("linkedin", "LinkedIn URL"),
        ("github", "GitHub URL"),
        ("portfolio", "Portfolio URL"),
    ]:
        url_val = personal.get(field, "").strip()
        if url_val and not validate_url(url_val):
            errors.append(f"{label} has an invalid URL format.")

    # 3. Minimum Content Check
    has_skills = any(len(v) > 0 for v in data.get("skills", {}).values())
    has_education = len(data.get("education", [])) > 0
    has_experience = len(data.get("experience", [])) > 0
    has_projects = len(data.get("projects", [])) > 0

    if not (has_skills or has_education or has_experience or has_projects):
        errors.append("Please provide at least some skills, education, experience, or projects.")

    return len(errors) == 0, errors

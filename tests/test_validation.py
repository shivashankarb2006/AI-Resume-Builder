"""
Unit tests for input validation and helper routines.
"""
import pytest
from utils.validation import (
    validate_email,
    validate_url,
    validate_phone,
    is_valid_date_str,
    clean_text,
)
from utils.helpers import (
    generate_resume_filename,
    split_lines_or_commas,
    format_bullet_point,
    sanitize_html,
)


def test_validate_email():
    # Valid emails
    valid, _ = validate_email("alex.chen@example.com")
    assert valid is True

    valid, _ = validate_email("john_doe123@sub.domain.org")
    assert valid is True

    # Invalid emails
    invalid, msg = validate_email("plainaddress")
    assert invalid is False
    assert "valid email" in msg

    invalid, msg = validate_email("missing@domain")
    assert invalid is False

    invalid, msg = validate_email("")
    assert invalid is False
    assert "required" in msg


def test_validate_url():
    # Valid URLs
    valid, url = validate_url("https://linkedin.com/in/alexchen")
    assert valid is True
    assert url == "https://linkedin.com/in/alexchen"

    # Prepending https if missing
    valid, url = validate_url("github.com/alexchen")
    assert valid is True
    assert url == "https://github.com/alexchen"

    # Optional empty URL
    valid, url = validate_url("", required=False)
    assert valid is True

    # Required empty URL
    valid, msg = validate_url("", required=True)
    assert valid is False

    # Unsafe javascript protocol
    valid, msg = validate_url("javascript:alert(1)")
    assert valid is False
    assert "Invalid URL" in msg


def test_validate_phone():
    valid, _ = validate_phone("+1 (555) 234-5678")
    assert valid is True

    valid, _ = validate_phone("555-123-4567")
    assert valid is True

    # Too short
    invalid, msg = validate_phone("12345")
    assert invalid is False
    assert "between 7 and 15" in msg

    # Optional empty
    valid, _ = validate_phone("", required=False)
    assert valid is True


def test_generate_resume_filename():
    assert generate_resume_filename("Alex Chen", "pdf") == "Alex_Chen_Resume.pdf"
    assert generate_resume_filename("Jane M. Doe, Jr.", "docx") == "Jane_M_Doe_Jr_Resume.docx"
    assert generate_resume_filename("", "pdf") == "Resume.pdf"
    assert generate_resume_filename("   ", "pdf") == "Resume.pdf"


def test_split_lines_or_commas():
    raw = "Python, Java, C++, TypeScript"
    items = split_lines_or_commas(raw)
    assert items == ["Python", "Java", "C++", "TypeScript"]

    raw_newlines = "Streamlit\nFlask\nFastAPI"
    items = split_lines_or_commas(raw_newlines)
    assert items == ["Streamlit", "Flask", "FastAPI"]

    assert split_lines_or_commas("") == []


def test_format_bullet_point():
    assert format_bullet_point("- developed a python script") == "Developed a python script."
    assert format_bullet_point("• engineered scalable backend") == "Engineered scalable backend."
    assert format_bullet_point("1. Optimized SQL database queries.") == "Optimized SQL database queries."
    assert format_bullet_point("") == ""


def test_sanitize_html():
    raw = "<script>alert('xss')</script>&"
    safe = sanitize_html(raw)
    assert "<script>" not in safe
    assert "&lt;script&gt;" in safe
    assert "&amp;" in safe

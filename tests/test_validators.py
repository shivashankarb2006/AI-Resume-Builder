"""
Unit tests for input validators
"""

from src.validators import validate_email, validate_url, sanitize_text, validate_profile


def test_validate_email():
    assert validate_email("user@example.com") is True
    assert validate_email("john.doe+work@domain.co.uk") is True
    assert validate_email("invalid-email") is False
    assert validate_email("user@") is False
    assert validate_email("@domain.com") is False
    assert validate_email("") is True  # Optional/empty is valid


def test_validate_url():
    assert validate_url("https://linkedin.com/in/username") is True
    assert validate_url("http://github.com/myrepo") is True
    assert validate_url("www.myportfolio.dev") is True
    assert validate_url("not a url") is False
    assert validate_url("") is True  # Optional/empty is valid


def test_sanitize_text():
    assert sanitize_text("  hello world  ") == "hello world"
    assert sanitize_text("test\x00data") == "testdata"
    assert sanitize_text("") == ""


def test_validate_profile():
    # Valid profile
    valid_data = {
        "personal_info": {
            "full_name": "Jane Doe",
            "email": "jane@example.com",
            "linkedin": "https://linkedin.com/in/janedoe",
        },
        "skills": {"programming_languages": ["Python"]},
        "education": [],
        "projects": [],
        "experience": [],
    }
    is_valid, errors = validate_profile(valid_data)
    assert is_valid is True
    assert len(errors) == 0

    # Incomplete profile (missing name and email)
    invalid_data = {
        "personal_info": {"full_name": "", "email": "bademail"},
        "skills": {},
        "education": [],
        "projects": [],
        "experience": [],
    }
    is_valid, errors = validate_profile(invalid_data)
    assert is_valid is False
    assert any("Full Name is required" in e for e in errors)
    assert any("not a valid email" in e for e in errors)

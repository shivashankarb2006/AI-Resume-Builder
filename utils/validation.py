"""
Validation helpers for user input in AI Resume Builder.
Ensures email, URL, phone, and dates meet standard formats without being over-restrictive.
"""
import re
from typing import Tuple

# Standard RFC 5322 compatible simplified email pattern
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)

# Standard URL pattern supporting http, https, or bare www/domain
URL_REGEX = re.compile(
    r"^(https?://)?([a-zA-Z0-9.-]+(\.[a-zA-Z]{2,}))(:[0-9]+)?(/.*)?$",
    re.IGNORECASE
)

# General phone regex accepting international prefixes, dashes, spaces, brackets
PHONE_REGEX = re.compile(
    r"^(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}$"
)


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate professional email address.
    Returns (is_valid, error_message).
    Empty string is considered valid if optional, handled at caller.
    """
    email = email.strip()
    if not email:
        return False, "Email address is required."
    if not EMAIL_REGEX.match(email):
        return False, "Please enter a valid email address (e.g., alex.chen@example.com)."
    return True, ""


def validate_url(url: str, required: bool = False) -> Tuple[bool, str]:
    """
    Validate web URL (LinkedIn, GitHub, Portfolio).
    Guards against unsafe protocols (javascript:, data:).
    Returns (is_valid, normalized_url).
    """
    url = url.strip()
    if not url:
        if required:
            return False, "URL is required."
        return True, ""

    lower_url = url.lower()
    if lower_url.startswith("javascript:") or lower_url.startswith("data:"):
        return False, "Invalid URL scheme."

    if not URL_REGEX.match(url):
        return False, "Please enter a valid URL (e.g., https://linkedin.com/in/username)."

    # Normalize by prepending https:// if protocol is missing
    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url

    return True, url


def validate_phone(phone: str, required: bool = False) -> Tuple[bool, str]:
    """
    Validate phone number.
    Returns (is_valid, message).
    """
    phone = phone.strip()
    if not phone:
        if required:
            return False, "Phone number is required."
        return True, ""

    # Strip formatting characters to check digit count
    digits = re.sub(r"\D", "", phone)
    if len(digits) < 7 or len(digits) > 15:
        return False, "Phone number should contain between 7 and 15 digits."

    return True, ""


def is_valid_date_str(date_str: str) -> bool:
    """Check if date or year string contains reasonable text."""
    date_str = date_str.strip()
    if not date_str:
        return True
    return len(date_str) <= 30


def clean_text(text: str) -> str:
    """Clean redundant spaces and normalize newlines."""
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in text.split("\n")]
    return "\n".join(lines).strip()

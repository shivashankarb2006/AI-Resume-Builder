"""
Unit tests for Claude API client and Prompt builders
"""

from src.prompts import (
    build_resume_generation_prompt,
    build_ats_analysis_prompt,
    RESUME_SYSTEM_PROMPT,
)
from src.claude_api import clean_json_response, get_mock_resume_data, call_claude_json


def test_clean_json_response():
    # Test markdown wrapped JSON
    raw_with_fences = '```json\n{"status": "ok", "score": 90}\n```'
    assert clean_json_response(raw_with_fences) == '{"status": "ok", "score": 90}'

    # Test plain JSON
    plain_json = '{"name": "Alex"}'
    assert clean_json_response(plain_json) == '{"name": "Alex"}'


def test_build_resume_prompt():
    dummy_data = {
        "personal_info": {"full_name": "Test User"},
        "skills": {"programming_languages": ["Python"]},
        "education": [],
        "projects": [],
        "experience": [],
    }
    prompt = build_resume_generation_prompt(dummy_data, "Software Engineer")
    assert "Test User" in prompt
    assert "REQUIRED JSON OUTPUT SCHEMA" in prompt
    assert "Never invent" in RESUME_SYSTEM_PROMPT


def test_mock_resume_generation():
    dummy_data = {
        "personal_info": {
            "full_name": "Sarah Connor",
            "professional_title": "AI Security Specialist",
            "email": "sarah@example.com",
        },
        "skills": {"programming_languages": "Python, Bash"},
        "education": [
            {
                "institution": "Tech University",
                "degree": "B.S.",
                "field_of_study": "Cybersecurity",
                "start_year": "2019",
                "end_year": "2023",
            }
        ],
        "projects": [
            {
                "name": "Sentinel",
                "description": "Network anomaly detector",
                "responsibilities": "Wrote packet sniffing algorithms",
                "results": "Identified 99% test anomalies",
            }
        ],
        "experience": [
            {
                "company": "CyberDyne",
                "role": "Security Intern",
                "responsibilities": "Penetration testing and reporting",
                "achievements": "Patched 3 high severity vulnerabilities",
                "technologies": "Python, Linux",
            }
        ],
        "certifications": [],
        "achievements": [],
    }

    mock_resume = get_mock_resume_data(dummy_data)
    assert mock_resume["personal_info"]["full_name"] == "Sarah Connor"
    assert len(mock_resume["experience"]) == 1
    assert len(mock_resume["experience"][0]["bullet_points"]) > 0
    assert len(mock_resume["projects"]) == 1
    assert "Sentinel" in mock_resume["projects"][0]["name"]


def test_missing_api_key_error_handling():
    # Without API key and without mock, it should return False with friendly message
    success, data, msg = call_claude_json(
        system_prompt="Test",
        user_prompt="Test",
        api_key="",
        mock_fallback=None,
    )
    assert success is False
    assert data is None
    assert "Claude API key is missing" in msg

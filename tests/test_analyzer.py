"""
Unit tests for ATS scoring heuristic and Job Description matcher.
"""
import pytest
from models.resume_schema import ResumeData, PersonalInfo
from utils.sample_data import get_sample_resume_data
from ai.analyzer import (
    calculate_ats_score,
    extract_skills_from_text,
    match_resume_with_job,
)


def test_calculate_ats_score_minimal():
    empty_resume = ResumeData()
    score_data = calculate_ats_score(empty_resume)
    assert score_data["total_score"] < 50
    assert "breakdown" in score_data
    assert "completeness" in score_data["breakdown"]


def test_calculate_ats_score_sample():
    sample = get_sample_resume_data()
    score_data = calculate_ats_score(sample)
    total = score_data["total_score"]
    # Sample has rich contact, education, skills, experience with action verbs, projects
    assert total >= 80
    assert "ATS Ready" in score_data["rating"] or "Strong" in score_data["rating"]

    # Verify score math consistency
    b = score_data["breakdown"]
    expected_sum = (
        b["completeness"]["score"]
        + b["action_verbs"]["score"]
        + b["skills_depth"]["score"]
        + b["hygiene"]["score"]
    )
    assert total == expected_sum


def test_extract_skills_from_text():
    sample_text = (
        "We are looking for a Software Engineer proficient in Python, Docker, and PostgreSQL. "
        "Experience with React, RESTful APIs, and Machine Learning is a plus."
    )
    skills = extract_skills_from_text(sample_text)
    skills_lower = [s.lower() for s in skills]
    assert "python" in skills_lower
    assert "docker" in skills_lower
    assert "postgresql" in skills_lower
    assert "react" in skills_lower


def test_match_resume_with_job():
    sample = get_sample_resume_data()
    jd = "Requires Python, Java, Docker, and Kubernetes with experience in Cloud computing."
    match = match_resume_with_job(sample, jd)

    assert "Python" in match["matching_skills"]
    assert "Docker" in match["matching_skills"]
    assert "Kubernetes" in match["missing_skills"]
    assert 0 < match["match_percentage"] < 100


def test_match_resume_empty_jd():
    sample = get_sample_resume_data()
    match = match_resume_with_job(sample, "")
    assert match["matching_skills"] == []
    assert match["missing_skills"] == []

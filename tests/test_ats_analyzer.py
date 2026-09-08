"""
Unit tests for ATS Analyzer and Keyword Matching
"""

from src.ats_analyzer import (
    extract_keywords_from_text,
    calculate_ats_score,
    analyze_ats_compatibility,
)


SAMPLE_PROFILE = {
    "personal_info": {
        "full_name": "Devin Torres",
        "email": "devin@example.com",
        "linkedin": "https://linkedin.com/in/devintorres",
        "github": "https://github.com/devintorres",
        "summary": "Full Stack Engineer with 3+ years writing Python, FastAPI, and Docker microservices.",
    },
    "skills": {
        "programming_languages": ["Python", "TypeScript"],
        "frameworks": ["FastAPI", "React"],
        "databases": ["PostgreSQL", "Redis"],
        "tools": ["Docker", "Git"],
    },
    "experience": [
        {
            "company": "CloudTech",
            "role": "Software Engineer",
            "responsibilities": "Built REST APIs with FastAPI and deployed containers to Docker.",
            "achievements": "Cut query latency by 25%.",
            "bullet_points": ["Architected scalable microservices using Python and Redis."],
        }
    ],
    "projects": [
        {
            "name": "DataHub",
            "technologies": "Python, PostgreSQL",
            "description": "Analytics dashboard",
            "bullet_points": ["Implemented user authentication and data pipelines."],
        }
    ],
    "education": [
        {"degree": "B.S.", "institution": "State University", "field_of_study": "CS"}
    ],
    "certifications": [{"name": "AWS Certified Cloud Practitioner"}],
    "achievements": ["Hackathon Runner-Up"],
}

JOB_DESCRIPTION = """
Senior Python Developer
Requirements:
- Strong experience with Python, FastAPI, and Docker.
- Experience with PostgreSQL and Redis.
- Knowledge of Kubernetes and AWS DynamoDB is a plus.
"""


def test_extract_keywords():
    text = "We are seeking a Python and Docker engineer who knows FastAPI and PostgreSQL."
    keywords = extract_keywords_from_text(text)
    assert "python" in keywords
    assert "docker" in keywords
    assert "fastapi" in keywords
    assert "postgresql" in keywords
    assert "java" not in keywords


def test_calculate_ats_score_with_job():
    analysis = calculate_ats_score(SAMPLE_PROFILE, JOB_DESCRIPTION)

    assert 0 <= analysis["overall_score"] <= 100
    assert "score_breakdown" in analysis
    assert len(analysis["matched_keywords"]) > 0
    # Python, FastAPI, Docker, PostgreSQL, Redis should be matched
    matched_lower = [k.lower() for k in analysis["matched_keywords"]]
    assert "python" in matched_lower
    assert "fastapi" in matched_lower
    assert "docker" in matched_lower

    # Kubernetes and DynamoDB should be missing
    missing_lower = [k.lower() for k in analysis["missing_keywords"]]
    assert "kubernetes" in missing_lower
    assert "dynamodb" in missing_lower


def test_calculate_ats_score_without_job():
    analysis = calculate_ats_score(SAMPLE_PROFILE, "")
    assert 0 <= analysis["overall_score"] <= 100
    assert len(analysis["matched_keywords"]) > 0
    assert len(analysis["missing_keywords"]) == 0  # No job means no missing job keywords


def test_analyze_ats_compatibility_demo():
    success, res, msg = analyze_ats_compatibility(
        SAMPLE_PROFILE,
        JOB_DESCRIPTION,
        demo_mode=True,
    )
    assert success is True
    assert "overall_score" in res
    assert "improvement_suggestions" in res
    assert len(res["improvement_suggestions"]) > 0

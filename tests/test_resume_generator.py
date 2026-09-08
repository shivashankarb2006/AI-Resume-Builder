"""
Unit tests for Resume Generator and Multi-Format Renderers
"""

from src.resume_generator import (
    format_resume_text,
    format_resume_markdown,
    format_resume_html,
    generate_resume_pipeline,
)


SAMPLE_STRUCTURED_RESUME = {
    "personal_info": {
        "full_name": "Marcus Vance",
        "professional_title": "Cloud Architect",
        "email": "marcus@example.com",
        "phone": "+1 555 999 8888",
        "location": "Seattle, WA",
        "linkedin": "https://linkedin.com/in/marcusvance",
        "github": "https://github.com/marcusvance",
    },
    "professional_summary": "Experienced Cloud Architect specializing in AWS and Kubernetes.",
    "skills": {
        "programming_languages": ["Python", "Go"],
        "tools": ["Docker", "Kubernetes", "Terraform"],
    },
    "experience": [
        {
            "company": "CloudCorp",
            "role": "Lead Architect",
            "duration": "2021 - Present",
            "location": "Seattle, WA",
            "bullet_points": [
                "Engineered resilient multi-region infrastructure on AWS.",
                "Automated CI/CD pipelines decreasing build failure by 40%.",
            ],
        }
    ],
    "projects": [
        {
            "name": "KubeDeploy",
            "technologies": "Go, Kubernetes API",
            "urls": "https://github.com/marcus/kubedeploy",
            "bullet_points": ["Created automated cluster deployment CLI."],
        }
    ],
    "education": [
        {
            "institution": "University of Washington",
            "degree": "B.S.",
            "field_of_study": "Computer Science",
            "year": "2017 - 2021",
            "gpa": "3.9",
            "highlights": "Dean's List",
        }
    ],
    "certifications": [
        {
            "name": "AWS Solutions Architect Professional",
            "organization": "AWS",
            "date": "2023",
        }
    ],
    "achievements": ["Speaker at KubeCon 2023"],
}


def test_format_resume_text():
    text = format_resume_text(SAMPLE_STRUCTURED_RESUME)
    assert "MARCUS VANCE" in text
    assert "PROFESSIONAL SUMMARY" in text
    assert "TECHNICAL SKILLS" in text
    assert "CloudCorp" in text
    assert "AWS Solutions Architect Professional" in text
    # Should not contain markdown headers
    assert "##" not in text


def test_format_resume_markdown():
    md = format_resume_markdown(SAMPLE_STRUCTURED_RESUME)
    assert "# Marcus Vance" in md
    assert "## Work Experience" in md
    assert "- **Programming Languages:** Python, Go" in md
    assert "### Lead Architect | CloudCorp" in md


def test_format_resume_html():
    html_out = format_resume_html(SAMPLE_STRUCTURED_RESUME)
    assert "<!DOCTYPE html>" in html_out
    assert "Marcus Vance" in html_out
    assert "CloudCorp" in html_out
    assert "KubeDeploy" in html_out
    assert "AWS Solutions Architect Professional" in html_out


def test_generate_resume_pipeline_demo_mode():
    raw_profile = {
        "personal_info": {
            "full_name": "Demo User",
            "email": "demo@user.com",
        },
        "skills": {"programming_languages": ["Python"]},
        "education": [],
        "projects": [
            {
                "name": "Test Project",
                "description": "A testing project",
                "responsibilities": "Building stuff",
                "results": "It worked",
            }
        ],
        "experience": [],
    }
    success, res, msg = generate_resume_pipeline(raw_profile, demo_mode=True)
    assert success is True
    assert res is not None
    assert "_rendered_text" in res
    assert "_rendered_markdown" in res
    assert "_rendered_html" in res

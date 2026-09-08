"""
AI Resume Builder - Claude API Client
Secure integration with Anthropic Claude models using the official Python SDK.
"""

import os
import re
import json
from typing import Dict, Any, Tuple, Optional
import anthropic
import streamlit as st

from src.prompts import (
    RESUME_SYSTEM_PROMPT,
    ATS_SYSTEM_PROMPT,
    build_resume_generation_prompt,
    build_ats_analysis_prompt,
)

# Recommended Claude models
PRIMARY_MODEL = "claude-3-5-sonnet-20241022"
FALLBACK_MODEL = "claude-3-haiku-20240307"


def get_api_key(custom_key: Optional[str] = None) -> Optional[str]:
    """
    Retrieve Anthropic API key safely with priority:
    1. Custom user-provided key (from UI input)
    2. Streamlit secrets (Streamlit Cloud deployment)
    3. OS Environment variables (.env local file)
    """
    if custom_key and custom_key.strip():
        return custom_key.strip()

    # Check Streamlit secrets (safe check to prevent KeyError)
    try:
        if hasattr(st, "secrets") and "ANTHROPIC_API_KEY" in st.secrets:
            return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass

    # Check local environment variables
    env_key = os.getenv("ANTHROPIC_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()

    return None


def clean_json_response(raw_text: str) -> str:
    """Extract valid JSON from raw text, removing any markdown code fences."""
    text = raw_text.strip()
    # Match ```json ... ``` or ``` ... ```
    pattern = r"^```(?:json)?\s*([\s\S]*?)\s*```$"
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    return text


def get_mock_resume_data(resume_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate realistic structured resume data offline for testing without API keys."""
    personal = resume_data.get("personal_info", {})
    raw_skills = resume_data.get("skills", {})

    # Format skills dict
    formatted_skills = {}
    for cat, val in raw_skills.items():
        if isinstance(val, list):
            formatted_skills[cat] = val
        elif isinstance(val, str):
            formatted_skills[cat] = [s.strip() for s in val.split(",") if s.strip()]
        else:
            formatted_skills[cat] = []

    # Format experience bullet points with action verbs
    formatted_exp = []
    for exp in resume_data.get("experience", []):
        if not exp.get("company") and not exp.get("role"):
            continue
        bullets = []
        if exp.get("responsibilities"):
            bullets.append(f"Spearheaded core development and execution of {exp['responsibilities'].lower().rstrip('.')}.")
        if exp.get("achievements"):
            bullets.append(f"Delivered tangible outcomes: {exp['achievements'].rstrip('.')}.")
        if exp.get("technologies"):
            bullets.append(f"Leveraged modern tech stack including {exp['technologies']}.")
        if not bullets:
            bullets.append("Contributed to engineering roadmap and cross-functional technical milestones.")

        formatted_exp.append(
            {
                "company": exp.get("company", "Company"),
                "role": exp.get("role", "Software Engineer"),
                "location": exp.get("location", ""),
                "duration": f"{exp.get('start_date', '')} - {exp.get('end_date', 'Present')}",
                "bullet_points": bullets,
            }
        )

    # Format projects bullet points
    formatted_proj = []
    for proj in resume_data.get("projects", []):
        if not proj.get("name"):
            continue
        p_bullets = []
        if proj.get("description"):
            p_bullets.append(f"Architected {proj['name']}: {proj['description'].rstrip('.')}.")
        if proj.get("responsibilities"):
            p_bullets.append(f"Engineered key components: {proj['responsibilities'].rstrip('.')}.")
        if proj.get("results"):
            p_bullets.append(f"Achieved verified impact: {proj['results'].rstrip('.')}.")
        if not p_bullets:
            p_bullets.append("Implemented full-stack architecture with production-ready standards.")

        urls = []
        if proj.get("github_url"):
            urls.append(f"GitHub: {proj['github_url']}")
        if proj.get("demo_url"):
            urls.append(f"Demo: {proj['demo_url']}")

        formatted_proj.append(
            {
                "name": proj.get("name", "Project"),
                "technologies": proj.get("technologies", ""),
                "urls": " | ".join(urls),
                "bullet_points": p_bullets,
            }
        )

    # Format education
    formatted_edu = []
    for edu in resume_data.get("education", []):
        if not edu.get("institution"):
            continue
        year_str = f"{edu.get('start_year', '')} - {edu.get('end_year', '')}".strip(" -")
        highlights = []
        if edu.get("coursework"):
            highlights.append(f"Coursework: {edu['coursework']}")
        if edu.get("achievements"):
            highlights.append(f"Honors: {edu['achievements']}")

        formatted_edu.append(
            {
                "institution": edu.get("institution", ""),
                "degree": edu.get("degree", ""),
                "field_of_study": edu.get("field_of_study", ""),
                "year": year_str,
                "gpa": edu.get("gpa", ""),
                "highlights": " | ".join(highlights),
            }
        )

    return {
        "personal_info": personal,
        "professional_summary": personal.get(
            "summary",
            f"Results-oriented {personal.get('professional_title', 'Software Engineer')} with a strong foundation in modern software engineering and software craftsmanship. Proven capability to design modular solutions and collaborate effectively in high-velocity teams.",
        ),
        "skills": formatted_skills,
        "experience": formatted_exp,
        "projects": formatted_proj,
        "education": formatted_edu,
        "certifications": resume_data.get("certifications", []),
        "achievements": [a for a in resume_data.get("achievements", []) if a.strip()],
    }


def call_claude_json(
    system_prompt: str,
    user_prompt: str,
    api_key: Optional[str] = None,
    mock_fallback: Optional[Dict[str, Any]] = None,
) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Execute an API call to Claude expecting a structured JSON response.
    Returns: (success: bool, data: Optional[dict], message: str)
    """
    resolved_key = get_api_key(api_key)

    # If no API key is provided, gracefully use mock fallback if supplied
    if not resolved_key:
        if mock_fallback is not None:
            return (
                True,
                mock_fallback,
                "Operating in Demo/Mock mode (No ANTHROPIC_API_KEY configured). Connect your Claude API key for live generation.",
            )
        return (
            False,
            None,
            "⚠️ Claude API key is missing. Please configure ANTHROPIC_API_KEY in your `.env` file, Streamlit secrets, or enter it in the sidebar.",
        )

    try:
        client = anthropic.Anthropic(api_key=resolved_key)

        # Attempt with primary model, fallback if unavailable
        try:
            response = client.messages.create(
                model=PRIMARY_MODEL,
                max_tokens=4000,
                temperature=0.2,  # Low temperature ensures precision and zero hallucination
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
        except anthropic.NotFoundError:
            # Fallback model
            response = client.messages.create(
                model=FALLBACK_MODEL,
                max_tokens=4000,
                temperature=0.2,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )

        # Parse response content
        raw_text = response.content[0].text
        cleaned_json = clean_json_response(raw_text)
        parsed_data = json.loads(cleaned_json)

        return True, parsed_data, "Generated successfully with Claude AI."

    except anthropic.AuthenticationError:
        return (
            False,
            None,
            "⚠️ Invalid Anthropic API Key. Please verify that your key starts with 'sk-ant-' and has active billing credits.",
        )
    except anthropic.RateLimitError:
        return (
            False,
            None,
            "⚠️ Claude API rate limit exceeded. Please wait a few moments before retrying.",
        )
    except anthropic.APIConnectionError:
        return (
            False,
            None,
            "⚠️ Connection to Anthropic API failed. Please check your internet connection.",
        )
    except json.JSONDecodeError as jde:
        return (
            False,
            None,
            f"⚠️ Claude response could not be parsed as valid JSON. Details: {str(jde)}",
        )
    except Exception as e:
        return False, None, f"⚠️ Unexpected error calling Claude API: {str(e)}"

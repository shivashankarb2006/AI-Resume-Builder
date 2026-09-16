"""
AI Resume Generator service.
Coordinates prompt assembly, local Ollama execution, and structured response parsing.
Includes safe recovery mechanisms for non-standard or malformed LLM outputs.
"""
import json
import logging
import re
from typing import List, Optional, Dict, Any

from models.resume_schema import (
    ResumeData,
    ExperienceEntry,
    ProjectEntry,
    TargetJob,
)
from utils.helpers import format_bullet_point
from .base import BaseAIProvider
from .prompts import (
    SUMMARY_GENERATION_SYSTEM_PROMPT,
    EXPERIENCE_BULLET_SYSTEM_PROMPT,
    PROJECT_BULLET_SYSTEM_PROMPT,
)

logger = logging.getLogger(__name__)


def _extract_json_from_text(raw_text: str) -> Optional[Dict[str, Any]]:
    """
    Robustly extract a JSON object from text that may contain markdown formatting or preamble.
    """
    if not raw_text:
        return None

    cleaned = raw_text.strip()
    # Strip markdown code fences if present
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    # Attempt direct json parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Search for first { and last }
    start_idx = cleaned.find("{")
    end_idx = cleaned.rfind("}")
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        candidate = cleaned[start_idx : end_idx + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    return None


def generate_professional_summary(
    resume_data: ResumeData,
    client: BaseAIProvider,
) -> str:
    """
    Generate an ATS-friendly, truthful professional summary grounded in user's data.
    """
    # Build context from user data
    edu_text = ""
    if resume_data.education:
        e = resume_data.education[0]
        edu_text = f"{e.degree} in {e.field_of_study} at {e.institution}"

    all_skills = []
    all_skills.extend(resume_data.skills.programming_languages)
    all_skills.extend(resume_data.skills.frameworks)
    all_skills.extend(resume_data.skills.ai_ml)
    all_skills.extend(resume_data.skills.databases)
    skills_text = ", ".join(all_skills[:10]) if all_skills else "General technical skills"

    exp_text = ""
    if resume_data.experience:
        roles = [f"{exp.role} at {exp.company}" for exp in resume_data.experience if not exp.is_empty()]
        exp_text = "; ".join(roles)

    proj_text = ""
    if resume_data.projects:
        projs = [p.name for p in resume_data.projects if not p.is_empty()]
        proj_text = ", ".join(projs)

    target_title = resume_data.target_job.title or "Software Engineer / Tech Professional"

    user_prompt = f"""Generate a professional summary for this candidate:
- Candidate Name: {resume_data.personal_info.full_name or 'Candidate'}
- Target Role: {target_title}
- Education: {edu_text or 'Undergraduate degree'}
- Key Skills: {skills_text}
- Experience: {exp_text or 'Academic & project experience'}
- Key Projects: {proj_text or 'Technical portfolio projects'}

Remember: Do NOT invent metrics or fake qualifications. Keep to 3-4 professional sentences.
"""

    try:
        response = client.generate(
            prompt=user_prompt,
            system_prompt=SUMMARY_GENERATION_SYSTEM_PROMPT,
            json_mode=False,
        )
        # Strip surrounding quotes if model wrapped summary in quotes
        summary = response.strip().strip('"').strip("'")
        
        # Clean common conversational LLM prefixes
        preamble_patterns = [
            r"^Here\s+(?:is|are)\s+(?:a\s+)?(?:concise\s+)?(?:professional\s+)?summary[^:\n]*:\s*",
            r"^Professional Summary:\s*",
            r"^Summary:\s*",
        ]
        for pat in preamble_patterns:
            summary = re.sub(pat, "", summary, flags=re.IGNORECASE).strip()
            
        return summary
    except Exception as e:
        logger.error(f"Summary generation error: {e}")
        raise e


def improve_experience_bullets(
    entry: ExperienceEntry,
    target_job: Optional[TargetJob],
    client: BaseAIProvider,
) -> List[str]:
    """
    Generate improved, ATS-optimized bullet points for a single work experience entry.
    """
    target_context = f"Target Role: {target_job.title}\n" if (target_job and target_job.title) else ""

    user_prompt = f"""{target_context}Company: {entry.company}
Role: {entry.role}
Location: {entry.location}
Candidate's Notes / Responsibilities:
{entry.responsibilities}
Candidate's Achievements:
{entry.achievements}

Transform these into 2-4 strong, action-oriented bullet points. Do not invent metrics or technologies not present in the user notes.
Return JSON with key "bullets".
"""

    try:
        raw_res = client.generate(
            prompt=user_prompt,
            system_prompt=EXPERIENCE_BULLET_SYSTEM_PROMPT,
            json_mode=True,
        )
        data = _extract_json_from_text(raw_res)
        if data and isinstance(data.get("bullets"), list):
            bullets = [format_bullet_point(b) for b in data["bullets"] if str(b).strip()]
            if bullets:
                return bullets

        # Fallback: line-by-line parsing if json extraction failed
        lines = [format_bullet_point(line) for line in raw_res.split("\n") if line.strip()]
        valid_lines = [l for l in lines if len(l) > 10 and not l.startswith("{") and not l.startswith("}")]
        return valid_lines[:4] if valid_lines else [entry.responsibilities]

    except Exception as e:
        logger.error(f"Error improving experience bullets: {e}")
        raise e


def improve_project_bullets(
    entry: ProjectEntry,
    target_job: Optional[TargetJob],
    client: BaseAIProvider,
) -> List[str]:
    """
    Generate improved, ATS-optimized bullet points for a project entry.
    """
    target_context = f"Target Role: {target_job.title}\n" if (target_job and target_job.title) else ""

    tech_list = ", ".join(entry.technologies) if entry.technologies else "Standard tools"

    user_prompt = f"""{target_context}Project: {entry.name}
Technologies Used: {tech_list}
Project Description: {entry.description}
Key Contributions: {entry.key_contributions}

Convert this into 2-3 strong ATS bullet points highlighting implementation and technical decisions. Do NOT fabricate numbers or claims.
Return JSON with key "bullets".
"""

    try:
        raw_res = client.generate(
            prompt=user_prompt,
            system_prompt=PROJECT_BULLET_SYSTEM_PROMPT,
            json_mode=True,
        )
        data = _extract_json_from_text(raw_res)
        if data and isinstance(data.get("bullets"), list):
            bullets = [format_bullet_point(b) for b in data["bullets"] if str(b).strip()]
            if bullets:
                return bullets

        lines = [format_bullet_point(line) for line in raw_res.split("\n") if line.strip()]
        valid_lines = [l for l in lines if len(l) > 10 and not l.startswith("{") and not l.startswith("}")]
        return valid_lines[:3] if valid_lines else [entry.description]

    except Exception as e:
        logger.error(f"Error improving project bullets: {e}")
        raise e

"""
ATS Analyzer and Job Description Matcher.
Provides a defensible, transparent heuristic scoring algorithm (0-100)
and identifies matching vs. missing skills without false fabrication.
"""
import re
from typing import Dict, List, Any, Optional, Set

from models.resume_schema import ResumeData, TargetJob
from .base import BaseAIProvider
from .prompts import RESUME_ANALYZER_PROMPT, JOB_DESCRIPTION_ANALYSIS_PROMPT
from .resume_generator import _extract_json_from_text

# Common high-impact action verbs valued by ATS and tech recruiters
ACTION_VERBS = {
    "architected", "automated", "built", "collaborated", "configured", "constructed",
    "created", "debugged", "deployed", "designed", "developed", "documented",
    "engineered", "enhanced", "established", "evaluated", "executed", "formulated",
    "implemented", "improved", "increased", "initiated", "integrated", "launched",
    "led", "maintained", "managed", "migrated", "monitored", "optimized",
    "orchestrated", "overhauled", "packaged", "performed", "pioneered", "planned",
    "programmed", "reduced", "refactored", "resolved", "restructured", "scaled",
    "simplified", "spearheaded", "standardized", "streamlined", "structured",
    "synthesized", "tested", "tracked", "trained", "transformed", "unified", "upgraded"
}

# Standard technology vocabulary dictionary for robust keyword extraction
KNOWN_TECH_VOCABULARY = {
    "python", "java", "c++", "c#", "c", "javascript", "typescript", "go", "rust",
    "ruby", "php", "swift", "kotlin", "scala", "html", "css", "sql", "nosql",
    "react", "angular", "vue", "next.js", "node.js", "express", "django", "flask",
    "fastapi", "spring", "spring boot", "asp.net", "streamlit", "tailwind",
    "git", "github", "gitlab", "docker", "kubernetes", "aws", "azure", "gcp",
    "linux", "bash", "postman", "jenkins", "terraform", "jira", "vs code",
    "postgresql", "postgres", "mysql", "mongodb", "redis", "sqlite", "oracle",
    "machine learning", "deep learning", "ai", "nlp", "llm", "rag", "langchain",
    "pytorch", "tensorflow", "scikit-learn", "pandas", "numpy", "opencv", "ollama",
    "rest", "restful", "api", "graphql", "microservices", "agile", "scrum", "ci/cd",
    "unit testing", "pytest", "junit", "data structures", "algorithms"
}


def calculate_ats_score(resume_data: ResumeData) -> Dict[str, Any]:
    """
    Calculates a transparent, defensible ATS Heuristic Score (0 - 100).
    Breakdown:
    1. Section Completeness (Max 25 pts)
    2. Action Verbs & Bullet Quality (Max 25 pts)
    3. Technical Skill Depth & Categorization (Max 25 pts)
    4. Contact & Format Hygiene (Max 25 pts)
    """
    breakdown = {}

    # 1. Section Completeness (25 pts max)
    completeness_score = 0
    comp_notes = []

    # Personal info completeness (max 8)
    p = resume_data.personal_info
    if p.full_name.strip():
        completeness_score += 2
    if p.email.strip():
        completeness_score += 2
    if p.phone.strip():
        completeness_score += 2
    if p.linkedin_url.strip() or p.github_url.strip():
        completeness_score += 2
    else:
        comp_notes.append("Add a LinkedIn or GitHub link for stronger tech ATS visibility.")

    # Summary (max 4)
    if resume_data.summary.strip():
        if len(resume_data.summary.split()) >= 20:
            completeness_score += 4
        else:
            completeness_score += 2
            comp_notes.append("Expand professional summary to 2-4 comprehensive sentences.")
    else:
        comp_notes.append("Missing professional summary.")

    # Education (max 5)
    valid_edu = [e for e in resume_data.education if not e.is_empty()]
    if valid_edu:
        completeness_score += 5
    else:
        comp_notes.append("No education entries provided.")

    # Experience & Projects (max 8)
    valid_exp = [e for e in resume_data.experience if not e.is_empty()]
    valid_proj = [p for p in resume_data.projects if not p.is_empty()]

    if valid_exp and valid_proj:
        completeness_score += 8
    elif valid_exp or valid_proj:
        completeness_score += 6
        comp_notes.append("Include both project work and work experience for maximum impact.")
    else:
        comp_notes.append("Missing both projects and work experience.")

    breakdown["completeness"] = {
        "score": min(25, completeness_score),
        "max": 25,
        "notes": comp_notes,
    }

    # 2. Action Verbs & Bullet Quality (25 pts max)
    all_bullets = []
    for exp in resume_data.experience:
        if exp.improved_bullets:
            all_bullets.extend(exp.improved_bullets)
        elif exp.responsibilities:
            all_bullets.extend(exp.responsibilities.split("\n"))
    for proj in resume_data.projects:
        if proj.improved_bullets:
            all_bullets.extend(proj.improved_bullets)
        elif proj.key_contributions:
            all_bullets.extend(proj.key_contributions.split("\n"))

    clean_bullets = [b.strip() for b in all_bullets if len(b.strip()) > 8]
    verb_count = 0
    bullet_notes = []

    if clean_bullets:
        for b in clean_bullets:
            first_word = re.sub(r"[^a-zA-Z]", "", b.split()[0]).lower()
            if first_word in ACTION_VERBS:
                verb_count += 1

        action_ratio = verb_count / len(clean_bullets)
        quality_score = int(action_ratio * 20)
        # Bonus for having at least 4 well-developed bullets
        if len(clean_bullets) >= 4:
            quality_score += 5

        quality_score = min(25, quality_score)
        if action_ratio < 0.6:
            bullet_notes.append(
                f"Only {int(action_ratio*100)}% of bullets start with strong action verbs. Use verbs like 'Engineered', 'Architected', 'Implemented'."
            )
    else:
        quality_score = 5
        bullet_notes.append("Add detailed bullet points to your experience and projects.")

    breakdown["action_verbs"] = {
        "score": quality_score,
        "max": 25,
        "notes": bullet_notes,
    }

    # 3. Technical Skill Depth & Categorization (25 pts max)
    skill_score = 0
    skill_notes = []
    s = resume_data.skills
    total_skills = len(s.programming_languages) + len(s.frameworks) + len(s.tools) + len(s.ai_ml) + len(s.databases)
    for c in s.custom_categories:
        total_skills += len(c.skills)

    if total_skills >= 10:
        skill_score += 15
    elif total_skills >= 5:
        skill_score += 10
    elif total_skills > 0:
        skill_score += 5
    else:
        skill_notes.append("Skills section is empty.")

    # Check categorization diversity
    categories_present = sum([
        bool(s.programming_languages),
        bool(s.frameworks),
        bool(s.tools),
        bool(s.databases or s.ai_ml or s.custom_categories),
    ])
    skill_score += categories_present * 2.5
    skill_score = min(25, int(skill_score))

    if categories_present < 3 and total_skills > 0:
        skill_notes.append("Organize skills into distinct categories (Languages, Frameworks, Tools, Databases).")

    breakdown["skills_depth"] = {
        "score": skill_score,
        "max": 25,
        "notes": skill_notes,
    }

    # 4. Contact & Format Hygiene (25 pts max)
    hygiene_score = 25
    hygiene_notes = []

    if "@" not in p.email:
        hygiene_score -= 10
        hygiene_notes.append("Valid contact email is missing or incorrect.")
    if not p.phone:
        hygiene_score -= 5
        hygiene_notes.append("Phone number is missing.")
    if not p.location:
        hygiene_score -= 5
        hygiene_notes.append("City/Location is recommended for location-based ATS filters.")

    breakdown["hygiene"] = {
        "score": max(0, hygiene_score),
        "max": 25,
        "notes": hygiene_notes,
    }

    total_score = (
        breakdown["completeness"]["score"]
        + breakdown["action_verbs"]["score"]
        + breakdown["skills_depth"]["score"]
        + breakdown["hygiene"]["score"]
    )

    return {
        "total_score": total_score,
        "breakdown": breakdown,
        "rating": (
            "Excellent (ATS Ready)" if total_score >= 85 else
            "Strong (Minor Polish Needed)" if total_score >= 70 else
            "Moderate (Improvements Recommended)" if total_score >= 50 else
            "Needs Improvement"
        ),
    }


def extract_skills_from_text(text: str) -> Set[str]:
    """
    Extract technical skills and keywords from raw text using vocabulary lookup.
    """
    if not text:
        return set()

    normalized = text.lower()
    found = set()

    for skill in KNOWN_TECH_VOCABULARY:
        # Match whole word or phrase boundaries
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, normalized):
            # Return proper display casing
            found.add(skill.title() if len(skill) > 3 else skill.upper())

    return found


def match_resume_with_job(
    resume_data: ResumeData,
    job_description: str,
) -> Dict[str, Any]:
    """
    Compares candidate's resume with the target job description.
    Identifies matching skills and missing/desired skills without encouraging fabrication.
    """
    if not job_description or not job_description.strip():
        return {
            "matching_skills": [],
            "missing_skills": [],
            "match_percentage": 0,
            "analysis": "No job description provided.",
        }

    # Extract all skills present in candidate's resume
    resume_text_corpus = []
    # Explicit skills
    s = resume_data.skills
    all_user_skills = set(
        [item.strip().lower() for item in s.programming_languages + s.frameworks + s.tools + s.ai_ml + s.databases]
    )
    for c in s.custom_categories:
        for sk in c.skills:
            all_user_skills.add(sk.strip().lower())

    # Text corpus from experience & projects
    for exp in resume_data.experience:
        resume_text_corpus.append(exp.company.lower())
        resume_text_corpus.append(exp.role.lower())
        resume_text_corpus.append(exp.responsibilities.lower())
        resume_text_corpus.append(exp.achievements.lower())
        resume_text_corpus.extend([b.lower() for b in exp.improved_bullets])

    for proj in resume_data.projects:
        resume_text_corpus.append(proj.name.lower())
        resume_text_corpus.append(proj.description.lower())
        resume_text_corpus.append(proj.key_contributions.lower())
        resume_text_corpus.extend([t.lower() for t in proj.technologies])
        resume_text_corpus.extend([b.lower() for b in proj.improved_bullets])

    full_resume_text = " ".join(resume_text_corpus)

    # Extract skills from job description
    jd_skills = extract_skills_from_text(job_description)

    matching = []
    missing = []

    for skill in jd_skills:
        skill_lower = skill.lower()
        # Direct skill match or presence in resume corpus
        if skill_lower in all_user_skills or skill_lower in full_resume_text:
            matching.append(skill)
        else:
            missing.append(skill)

    total_jd_skills = len(matching) + len(missing)
    match_percentage = int((len(matching) / total_jd_skills) * 100) if total_jd_skills > 0 else 100

    return {
        "matching_skills": sorted(matching),
        "missing_skills": sorted(missing),
        "match_percentage": match_percentage,
        "total_skills_detected": total_jd_skills,
    }


def analyze_resume_with_ai(
    resume_data: ResumeData,
    client: BaseAIProvider,
) -> Dict[str, Any]:
    """
    Use local LLM to perform contextual qualitative resume review.
    """
    # Build concise summary of the candidate's resume for the model
    skills_summary = ", ".join(
        resume_data.skills.programming_languages +
        resume_data.skills.frameworks +
        resume_data.skills.tools
    )
    exp_summary = "\n".join([f"- {e.role} at {e.company}: {e.responsibilities}" for e in resume_data.experience])
    proj_summary = "\n".join([f"- {p.name}: {p.description}" for p in resume_data.projects])

    prompt = f"""Evaluate this resume:
Target Job: {resume_data.target_job.title or 'General Tech Role'}
Job Description: {resume_data.target_job.job_description[:600] or 'Not provided'}
Professional Summary: {resume_data.summary or 'None'}
Technical Skills: {skills_summary or 'None'}
Experience:
{exp_summary or 'None'}
Projects:
{proj_summary or 'None'}

Return your assessment strictly as JSON with keys: 'strengths', 'weaknesses', 'formatting_risks', 'tailoring_advice'.
"""

    try:
        raw_res = client.generate(
            prompt=prompt,
            system_prompt=RESUME_ANALYZER_PROMPT,
            json_mode=True,
        )
        data = _extract_json_from_text(raw_res)
        if data and isinstance(data, dict):
            return {
                "strengths": data.get("strengths", []),
                "weaknesses": data.get("weaknesses", []),
                "formatting_risks": data.get("formatting_risks", ["None detected"]),
                "tailoring_advice": data.get("tailoring_advice", []),
            }
    except Exception:
        pass

    # Fallback default feedback if model is offline or returns invalid format
    return {
        "strengths": ["Clear structure and standard resume sections present."],
        "weaknesses": ["Consider adding further quantifiable metrics to project outcomes where available."],
        "formatting_risks": ["None detected. Clean standard layout."],
        "tailoring_advice": ["Align resume vocabulary with keywords in your target job posting."],
    }

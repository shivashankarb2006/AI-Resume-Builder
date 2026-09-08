"""
AI Resume Builder - Prompt Engineering & Prompt Templates
Contains structured prompts for Resume Generation and ATS Analysis.
"""

import json
from typing import Dict, Any

# ==============================================================================
# SYSTEM PROMPT: RESUME GENERATION (STRICT ANTI-HALLUCINATION RULES)
# ==============================================================================
RESUME_SYSTEM_PROMPT = """You are an expert ATS (Applicant Tracking System) resume writer and executive career coach.

Your task is to craft an ATS-compliant, highly professional resume using ONLY the factual information supplied by the candidate.

CRITICAL RULES (NON-NEGOTIABLE):
1. FACTUAL HONESTY: Never invent companies, job titles, education, certifications, degrees, or skills.
2. NO FABRICATED METRICS: Never fabricate numerical percentages, dollar amounts, or metric achievements (e.g., do NOT invent "boosted sales by 40%" or "reduced latency by 90%" unless the candidate explicitly provided those numbers).
3. NO INVENTED SKILLS: Never claim or list a skill or tool that the candidate did not mention, even if it is explicitly demanded by the target job description.
4. ACTION VERBS: Begin every bullet point with a strong, precise past-tense action verb (e.g., "Engineered", "Implemented", "Architected", "Automated", "Spearheaded", "Analyzed").
5. ATS OPTIMIZATION: Use clean, standard terminology. Avoid tables, icons, graphics, emojis, or non-standard characters.
6. TARGET ALIGNMENT: If a target job description is provided, prioritize and highlight the candidate's GENUINE experiences and skills that align with the job's priorities.
7. OUTPUT FORMAT: You must return ONLY valid, parseable JSON matching the exact schema requested. Do not include markdown commentary, chat preamble, or postscript outside the JSON block.
"""

# ==============================================================================
# SYSTEM PROMPT: ATS COMPATIBILITY & KEYWORD ANALYSIS
# ==============================================================================
ATS_SYSTEM_PROMPT = """You are a senior technical recruiter and ATS parsing algorithm specialist.

Analyze the candidate's resume data against the provided target job description.
Evaluate keyword overlap, skill presence, experience relevance, and structural clarity.

CRITICAL RULES:
1. Objectively identify keywords and skills explicitly found in the target job description.
2. Accurately categorize which keywords the candidate HAS vs which keywords are MISSING from their profile.
3. NEVER tell the candidate to lie. For missing keywords, advise: "Consider adding this skill if you genuinely have experience with it."
4. Provide constructive, actionable resume improvement suggestions.
5. You must return ONLY valid, parseable JSON matching the exact schema requested.
"""


def build_resume_generation_prompt(resume_data: Dict[str, Any], target_job: str = "") -> str:
    """Build user prompt requesting structured JSON for resume generation."""
    return f"""Please generate an ATS-optimized resume based strictly on the candidate profile below.

CANDIDATE DATA:
{json.dumps(resume_data, indent=2)}

TARGET JOB DESCRIPTION:
{target_job if target_job.strip() else "None provided (Optimize for general industry standards based on candidate title)."}

REQUIRED JSON OUTPUT SCHEMA:
{{
  "personal_info": {{
    "full_name": "string",
    "professional_title": "string",
    "email": "string",
    "phone": "string",
    "location": "string",
    "linkedin": "string",
    "github": "string",
    "portfolio": "string"
  }},
  "professional_summary": "Concise 3-4 sentence summary emphasizing candidate strengths aligned with target role without fabricating anything.",
  "skills": {{
    "programming_languages": ["skill1", "skill2"],
    "frameworks": ["lib1", "lib2"],
    "databases": ["db1"],
    "tools": ["tool1", "tool2"],
    "soft_skills": ["skill1", "skill2"]
  }},
  "experience": [
    {{
      "company": "string",
      "role": "string",
      "location": "string",
      "duration": "e.g. Jun 2023 - Sep 2023",
      "bullet_points": [
        "Strong action-verb bullet point converting candidate responsibilities into impact",
        "Second bullet point emphasizing tools and actual verified achievements"
      ]
    }}
  ],
  "projects": [
    {{
      "name": "string",
      "technologies": "string",
      "urls": "GitHub / Demo link if provided",
      "bullet_points": [
        "Action-oriented bullet detailing architecture and implementation",
        "Action-oriented bullet detailing impact using only supplied data"
      ]
    }}
  ],
  "education": [
    {{
      "institution": "string",
      "degree": "string",
      "field_of_study": "string",
      "year": "string",
      "gpa": "string (omit if empty)",
      "highlights": "Coursework or honors provided"
    }}
  ],
  "certifications": [
    {{
      "name": "string",
      "organization": "string",
      "date": "string",
      "url": "string"
    }}
  ],
  "achievements": [
    "Achievement or award bullet"
  ]
}}

Remember: Return ONLY valid JSON.
"""


def build_ats_analysis_prompt(resume_data: Dict[str, Any], target_job: str) -> str:
    """Build user prompt requesting structured JSON for ATS compatibility scoring."""
    return f"""Please perform an in-depth ATS compatibility analysis between this candidate's profile and the target job description.

CANDIDATE DATA:
{json.dumps(resume_data, indent=2)}

TARGET JOB DESCRIPTION:
{target_job}

REQUIRED JSON OUTPUT SCHEMA:
{{
  "overall_score": 85,
  "score_breakdown": {{
    "keyword_match": {{ "score": 22, "max_score": 25, "label": "Keyword Match" }},
    "skills_match": {{ "score": 23, "max_score": 25, "label": "Skills Alignment" }},
    "experience_relevance": {{ "score": 18, "max_score": 20, "label": "Experience Relevance" }},
    "resume_structure": {{ "score": 14, "max_score": 15, "label": "Formatting & Structure" }},
    "completeness": {{ "score": 13, "max_score": 15, "label": "Profile Completeness" }}
  }},
  "matched_skills": ["Python", "FastAPI", "Docker", "pytest"],
  "missing_skills": ["Kubernetes", "AWS DynamoDB"],
  "matched_keywords": ["REST API", "Microservices", "Unit Testing", "CI/CD"],
  "missing_keywords": ["Distributed Caching", "GraphQL"],
  "improvement_suggestions": [
    "Highlight your experience with unit testing in your DocuChat project to better match the job posting requirements.",
    "Consider adding Kubernetes if you have personal or academic experience with container orchestration."
  ],
  "summary_verdict": "Strong candidate alignment for AI/Python engineering roles with notable strength in core backend frameworks."
}}

Remember: Return ONLY valid JSON.
"""

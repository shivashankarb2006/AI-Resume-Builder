"""
AI Resume Builder - ATS Compatibility & Keyword Analyzer Engine
Evaluates keyword overlap, skills relevance, experience alignment, and structural completeness.
"""

import re
from typing import Dict, Any, List, Set, Tuple, Optional
from src.prompts import ATS_SYSTEM_PROMPT, build_ats_analysis_prompt
from src.claude_api import get_api_key, call_claude_json

# Standard tech and software industry keyword dictionary for robust matching
COMMON_TECH_KEYWORDS = {
    # Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "golang", "go", "ruby", "php", "rust", "swift", "kotlin", "scala", "sql", "html", "css", "bash", "shell",
    # Frameworks & Libraries
    "react", "angular", "vue", "next.js", "node.js", "express", "django", "flask", "fastapi", "spring", "spring boot", "asp.net", "rails", "streamlit",
    "pandas", "numpy", "pytorch", "tensorflow", "scikit-learn", "keras", "langchain", "huggingface", "opencv",
    # Databases & Caching
    "postgresql", "postgres", "mysql", "mongodb", "sqlite", "redis", "elasticsearch", "cassandra", "dynamodb", "oracle", "mariadb", "firebase", "supabase",
    # DevOps & Cloud
    "docker", "kubernetes", "aws", "amazon web services", "azure", "gcp", "google cloud", "terraform", "ansible", "ci/cd", "github actions", "jenkins", "git", "linux", "unix", "nginx", "kafka",
    # Concepts & Practices
    "rest api", "restful", "graphql", "microservices", "agile", "scrum", "unit testing", "pytest", "test driven development", "tdd", "system design", "distributed systems", "rag", "large language models", "llm", "machine learning", "deep learning", "nlp", "computer vision", "object-oriented programming", "oop",
}


def extract_keywords_from_text(text: str) -> Set[str]:
    """Extract recognized technical keywords and key terms from arbitrary text."""
    if not text:
        return set()

    # Replace common trailing/enclosing punctuation with spaces
    cleaned = re.sub(r"[,;:\!\?\(\)\[\]\{\}\"\'\“\”\/]", " ", text.lower())
    # Replace sentence-ending periods with spaces (preserving internal dots like node.js)
    cleaned = re.sub(r"\.(?=\s|$)", " ", cleaned)
    padded = f" {cleaned} "

    found_keywords = set()
    for kw in COMMON_TECH_KEYWORDS:
        pattern = rf"(?:\s|^){re.escape(kw)}(?:\s|$)"
        if re.search(pattern, padded):
            found_keywords.add(kw)

    return found_keywords


def extract_all_resume_text(resume_data: Dict[str, Any]) -> str:
    """Consolidate all candidate resume fields into a single searchable string."""
    chunks = []
    p = resume_data.get("personal_info", {})
    chunks.extend([p.get("full_name", ""), p.get("professional_title", ""), p.get("summary", "")])

    # Skills
    for v in resume_data.get("skills", {}).values():
        if isinstance(v, list):
            chunks.extend(v)
        elif isinstance(v, str):
            chunks.append(v)

    # Experience
    for exp in resume_data.get("experience", []):
        chunks.extend([
            exp.get("company", ""),
            exp.get("role", ""),
            exp.get("responsibilities", ""),
            exp.get("achievements", ""),
            exp.get("technologies", ""),
        ])
        for bp in exp.get("bullet_points", []):
            chunks.append(bp)

    # Projects
    for proj in resume_data.get("projects", []):
        chunks.extend([
            proj.get("name", ""),
            proj.get("description", ""),
            proj.get("responsibilities", ""),
            proj.get("results", ""),
            proj.get("technologies", ""),
        ])
        for bp in proj.get("bullet_points", []):
            chunks.append(bp)

    # Education
    for edu in resume_data.get("education", []):
        chunks.extend([
            edu.get("institution", ""),
            edu.get("degree", ""),
            edu.get("field_of_study", ""),
            edu.get("coursework", ""),
            edu.get("achievements", ""),
            edu.get("highlights", ""),
        ])

    # Certifications & Achievements
    for cert in resume_data.get("certifications", []):
        chunks.extend([cert.get("name", ""), cert.get("organization", "")])

    for ach in resume_data.get("achievements", []):
        if isinstance(ach, str):
            chunks.append(ach)

    return " ".join(chunks)


def calculate_ats_score(
    resume_data: Dict[str, Any],
    target_job: str = "",
) -> Dict[str, Any]:
    """
    Perform deterministic rule-based ATS analysis with granular scoring breakdown.
    Provides instant offline results and transparent scoring metrics.
    """
    resume_text = extract_all_resume_text(resume_data)
    resume_keywords = extract_keywords_from_text(resume_text)

    job_keywords = extract_keywords_from_text(target_job) if target_job.strip() else set()

    if job_keywords:
        matched_kws = sorted(list(job_keywords.intersection(resume_keywords)))
        missing_kws = sorted(list(job_keywords.difference(resume_keywords)))
        keyword_match_ratio = len(matched_kws) / len(job_keywords) if job_keywords else 1.0
    else:
        # Fallback when no job description is supplied: score based on verified technical keyword density
        matched_kws = sorted(list(resume_keywords))
        missing_kws = []
        keyword_match_ratio = min(len(matched_kws) / 8.0, 1.0)

    # 1. Keyword Match (Max 25 pts)
    kw_score = round(keyword_match_ratio * 25)

    # 2. Skills Match (Max 25 pts)
    # Check if candidate provided languages, frameworks, databases, tools
    skills_dict = resume_data.get("skills", {})
    categories_filled = sum(1 for v in skills_dict.values() if (isinstance(v, list) and v) or (isinstance(v, str) and v.strip()))
    skills_score = min(round((categories_filled / 4.0) * 20 + (len(matched_kws) > 3) * 5), 25)

    # 3. Experience & Projects Relevance (Max 20 pts)
    has_exp = len(resume_data.get("experience", [])) > 0
    has_proj = len(resume_data.get("projects", [])) > 0
    # Check for measurable numbers in text (e.g. percentages or numbers)
    has_metrics = bool(re.search(r"\b\d+[\%kKmM\+]?\b", resume_text))
    exp_score = (10 if has_exp else 4) + (6 if has_proj else 2) + (4 if has_metrics else 0)
    exp_score = min(exp_score, 20)

    # 4. Resume Structure & Formatting (Max 15 pts)
    # Checks contact completeness (email, phone, linkedin/github)
    p = resume_data.get("personal_info", {})
    has_contact = bool(p.get("email") and (p.get("linkedin") or p.get("github")))
    has_summary = bool(p.get("summary") or resume_data.get("professional_summary"))
    has_edu = len(resume_data.get("education", [])) > 0

    struct_score = (6 if has_contact else 2) + (5 if has_summary else 1) + (4 if has_edu else 1)
    struct_score = min(struct_score, 15)

    # 5. Profile Completeness (Max 15 pts)
    has_certs = len(resume_data.get("certifications", [])) > 0
    has_ach = len(resume_data.get("achievements", [])) > 0
    comp_score = 7 + (4 if has_certs else 0) + (4 if has_ach else 0)
    comp_score = min(comp_score, 15)

    # Total Score out of 100
    total_score = kw_score + skills_score + exp_score + struct_score + comp_score

    # Generate Actionable Suggestions
    suggestions: List[str] = []

    if missing_kws:
        top_missing = ", ".join([k.upper() if len(k) <= 3 else k.title() for k in missing_kws[:4]])
        suggestions.append(
            f"The job description requests {top_missing}. Consider adding these skills to your profile if you genuinely have experience with them."
        )

    if not has_metrics:
        suggestions.append("Add measurable outcomes (e.g., reduced latency by 30%, served 500+ users) where you have genuine metrics.")

    if not p.get("github") and not p.get("portfolio"):
        suggestions.append("Include your GitHub repository or live portfolio URL to provide recruiters with verifiable proof of your work.")

    if not has_summary:
        suggestions.append("Add a concise 2-3 sentence Professional Summary at the top of your resume highlighting your core specialization.")

    if not has_certs:
        suggestions.append("Consider adding recognized certifications (e.g., AWS, Azure, Google Cloud, Coursera) to strengthen credibility.")

    if not suggestions:
        suggestions.append("Excellent profile alignment! Your resume satisfies ATS standard criteria.")

    # Format human-friendly capitalized keywords
    def format_kw(k):
        return k.upper() if len(k) <= 3 or k in ["aws", "gcp", "sql", "api", "tdd", "rag", "llm", "oop", "nlp", "ci/cd"] else k.title()

    formatted_matched = [format_kw(k) for k in matched_kws]
    formatted_missing = [format_kw(k) for k in missing_kws]

    return {
        "overall_score": total_score,
        "score_breakdown": {
            "keyword_match": {"score": kw_score, "max_score": 25, "label": "Keyword Match"},
            "skills_match": {"score": skills_score, "max_score": 25, "label": "Skills Alignment"},
            "experience_relevance": {"score": exp_score, "max_score": 20, "label": "Experience Relevance"},
            "resume_structure": {"score": struct_score, "max_score": 15, "label": "Formatting & Structure"},
            "completeness": {"score": comp_score, "max_score": 15, "label": "Profile Completeness"},
        },
        "matched_keywords": formatted_matched,
        "missing_keywords": formatted_missing,
        "improvement_suggestions": suggestions,
        "summary_verdict": (
            "Outstanding ATS alignment! Your profile demonstrates strong keyword presence and comprehensive section coverage."
            if total_score >= 80
            else "Good profile foundation with clear opportunities to incorporate targeted job keywords and measurable impact."
            if total_score >= 60
            else "Needs improvement. Incorporate missing core requirements and flesh out technical experience bullets."
        ),
    }


def analyze_ats_compatibility(
    resume_data: Dict[str, Any],
    target_job: str = "",
    custom_api_key: Optional[str] = None,
    use_ai: bool = True,
    demo_mode: bool = False,
) -> Tuple[bool, Dict[str, Any], str]:
    """
    Master ATS Analysis function:
    1. Computes deterministic baseline score.
    2. If AI is enabled and API key is present, enriches with Claude AI semantic feedback.
    """
    baseline_analysis = calculate_ats_score(resume_data, target_job)

    # If demo mode or no target job or AI disabled, return deterministic analysis immediately
    if demo_mode or not target_job.strip() or not use_ai:
        return True, baseline_analysis, "ATS analysis completed successfully (Deterministic Rule Engine)."

    active_key = get_api_key(custom_api_key)
    if not active_key:
        return True, baseline_analysis, "ATS analysis completed successfully (Offline Rules)."

    # Call Claude for deep semantic evaluation
    try:
        user_prompt = build_ats_analysis_prompt(resume_data, target_job)
        success, ai_result, msg = call_claude_json(
            system_prompt=ATS_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            api_key=active_key,
            mock_fallback=baseline_analysis,
        )
        if success and ai_result and "overall_score" in ai_result:
            return True, ai_result, "ATS analysis completed with Claude AI."
    except Exception:
        pass

    # Safe fallback to deterministic analysis
    return True, baseline_analysis, "ATS analysis completed with deterministic rule engine."

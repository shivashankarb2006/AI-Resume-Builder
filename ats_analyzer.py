import ollama
import json
import re


MODEL_NAME = "llama3.2"


def analyze_resume(resume, job_description):

    prompt = f"""
You are an ATS resume analysis expert.

Analyze the candidate resume against the job description.

IMPORTANT RULES:

1. Do not invent information.
2. Do not assume the candidate has skills that are not present.
3. Base the analysis only on the resume and job description.
4. Give an ATS compatibility score from 0 to 100.
5. Identify important keywords present in both.
6. Identify important job-description keywords missing from the resume.
7. Give practical suggestions for improving the resume.
8. Do not suggest lying or adding skills the candidate does not have.
9. Keep the analysis concise and useful.

Return ONLY valid JSON using exactly this structure:

{{
    "score": 0,
    "matching_keywords": [],
    "missing_keywords": [],
    "suggestions": []
}}

RESUME:

{resume}

--------------------------------------------------

JOB DESCRIPTION:

{job_description}

--------------------------------------------------

Analyze now.
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    result = response["message"]["content"].strip()

    # -----------------------------------------------------
    # Remove markdown JSON fences if AI adds them
    # -----------------------------------------------------

    result = result.replace("```json", "")
    result = result.replace("```", "")
    result = result.strip()

    # -----------------------------------------------------
    # Try direct JSON parsing
    # -----------------------------------------------------

    try:

        return json.loads(result)

    except json.JSONDecodeError:

        # -------------------------------------------------
        # Try extracting JSON from the response
        # -------------------------------------------------

        match = re.search(
            r"\{.*\}",
            result,
            re.DOTALL
        )

        if match:

            try:

                return json.loads(
                    match.group(0)
                )

            except json.JSONDecodeError:
                pass

    # -----------------------------------------------------
    # Fallback
    # -----------------------------------------------------

    return {
        "score": 0,
        "matching_keywords": [],
        "missing_keywords": [],
        "suggestions": [
            "Unable to analyze the resume. Please try again."
        ]
    }
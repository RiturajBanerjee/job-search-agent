# backend/modules/jd_analyzer.py
import logging
import json
import google.generativeai as genai
from config import settings

logger = logging.getLogger(__name__)

genai.configure(api_key=settings.gemini_api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

EXTRACTION_PROMPT = """
You are a job description parser and role matcher.

The user is searching for: "{search_role}"
The job posting title is: "{job_title}"

Analyze the job description and return ONLY a valid JSON object with exactly these fields:

{{
  "role_is_match": <true if the job title is the same role or a close equivalent to the search role, false if clearly different>,
  "role_match_reason": <short string explaining why it matches or not>,
  "min_years_experience": <integer or null>,
  "max_years_experience": <integer or null>,
  "domains": <list of domain strings e.g. ["fintech", "saas", "b2b"]>,
  "seniority_level": <"junior" | "mid" | "senior" | "lead" | "director" | "unknown">,
  "key_skills": <list of up to 5 important skills mentioned>,
  "remote_friendly": <true | false | null>
}}

Examples of role matches (role_is_match = true):
- Search: "software engineer", Job: "associate software engineer" → true
- Search: "software engineer", Job: "software development engineer" → true
- Search: "software engineer", Job: "SDE II" → true
- Search: "product manager", Job: "associate product manager" → true
- Search: "product manager", Job: "product owner" → true (close equivalent)
- Search: "data scientist", Job: "ML engineer" → true (close equivalent)

Examples of non-matches (role_is_match = false):
- Search: "software engineer", Job: "engineering manager" → false (management, not IC)
- Search: "product manager", Job: "project manager" → false (different discipline)
- Search: "data scientist", Job: "data entry specialist" → false

Job Description:
{jd_text}
"""

def extract_jd_requirements(jd_text: str, search_role: str, job_title: str) -> dict:
    """Call Gemini to extract JD requirements AND check if role matches semantically."""
    if not jd_text or len(jd_text.strip()) < 50:
        logger.warning("JD text too short, skipping LLM extraction")
        return {
            "role_is_match": True,  # give benefit of doubt if no JD
            "role_match_reason": "No JD text available",
            "min_years_experience": None,
            "max_years_experience": None,
            "domains": [],
            "seniority_level": "unknown",
            "key_skills": [],
            "remote_friendly": None,
        }

    prompt = EXTRACTION_PROMPT.format(
        search_role=search_role,
        job_title=job_title,
        jd_text=jd_text[:10000]
    )
    raw = ""
    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()

        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        extracted = json.loads(raw)
        logger.info(
            f"Role match: {extracted.get('role_is_match')} "
            f"({extracted.get('role_match_reason')}) | "
            f"Exp: {extracted.get('min_years_experience')}-{extracted.get('max_years_experience')} yrs"
        )
        return extracted

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM JSON: {e} | Raw: {raw}")
        return {
            "role_is_match": True,
            "role_match_reason": "Parse error - defaulting to match",
            "min_years_experience": None, "max_years_experience": None,
            "domains": [], "seniority_level": "unknown",
            "key_skills": [], "remote_friendly": None
        }
    except Exception as e:
        logger.error(f"Gemini API call failed: {e}")
        raise


def analyze_match(job: dict, years_exp: int, search_role: str, domain: str = None) -> dict:
    """Score a job against user profile. Returns score 0-100 and match details."""
    jd_text = job.get("description", "")
    job_title = job.get("title", "")

    requirements = extract_jd_requirements(jd_text, search_role, job_title)

    score = 0
    reasons = []
    warnings = []

    # --- Role match (gate check) ---
    # If LLM says it's a completely different role, score 0 and exit early
    if not requirements.get("role_is_match", True):
        logger.info(f"Role mismatch — skipping: {requirements.get('role_match_reason')}")
        return {
            "score": 0,
            "is_role_match": False,
            "reasons": [],
            "warnings": [f"Role mismatch: {requirements.get('role_match_reason')}"],
            "extracted_requirements": requirements,
            "job": job,
        }

    score += 25  # base score for being a matching role
    reasons.append(f"Role match: {requirements.get('role_match_reason')}")

    # --- Experience match ---
    min_exp = requirements.get("min_years_experience")
    max_exp = requirements.get("max_years_experience")

    if min_exp is not None:
        if years_exp >= min_exp:
            score += 35
            reasons.append(f"Experience OK: you have {years_exp} yrs, JD needs {min_exp}+")
        elif years_exp >= min_exp - 1:
            score += 20
            warnings.append(f"Slightly under: JD wants {min_exp} yrs, you have {years_exp}")
        else:
            warnings.append(f"Under-qualified: JD wants {min_exp} yrs, you have {years_exp}")
    else:
        score += 15
        reasons.append("No specific experience requirement in JD")

    if max_exp is not None and years_exp > max_exp + 2:
        score -= 10
        warnings.append(f"Possibly over-qualified: JD cap is {max_exp} yrs")

    # --- Domain match ---
    if domain:
        jd_domains = [d.lower() for d in requirements.get("domains", [])]
        user_domain = domain.lower()
        if any(user_domain in d or d in user_domain for d in jd_domains):
            score += 25
            reasons.append(f"Domain match: '{domain}' in JD domains {jd_domains}")
        else:
            warnings.append(f"Domain '{domain}' not in JD (JD domains: {jd_domains})")

    # --- Seniority alignment ---
    seniority = requirements.get("seniority_level", "unknown")
    seniority_exp_map = {
        "junior": (0, 3), "mid": (2, 6), "senior": (5, 12),
        "lead": (7, 15), "director": (10, 30)
    }
    if seniority in seniority_exp_map:
        low, high = seniority_exp_map[seniority]
        if low <= years_exp <= high:
            score += 15
            reasons.append(f"Seniority '{seniority}' aligns with your {years_exp} yrs")
        else:
            warnings.append(f"Seniority mismatch: '{seniority}' typically needs {low}-{high} yrs")

    score = max(0, min(score, 100))
    logger.info(f"'{job_title}' | Score: {score}/100 | Reasons: {reasons} | Warnings: {warnings}")

    return {
        "score": score,
        "is_role_match": True,
        "reasons": reasons,
        "warnings": warnings,
        "extracted_requirements": requirements,
        "job": job,
    }
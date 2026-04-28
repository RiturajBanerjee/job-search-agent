import json
import pytest
from unittest.mock import patch, MagicMock
from modules.jd_analyzer import extract_jd_requirements, analyze_match

MOCK_REQUIREMENTS = {
    "role_is_match": True,
    "role_match_reason": "Senior PM is a direct match for product manager",
    "min_years_experience": 5,
    "max_years_experience": 8,
    "domains": ["fintech", "saas", "b2b"],
    "seniority_level": "senior",
    "key_skills": ["roadmap", "stakeholders", "data analysis"],
    "remote_friendly": True,
}

@patch("modules.jd_analyzer.model")
def test_extract_jd_requirements_success(mock_model):
    mock_resp = MagicMock()
    mock_resp.text = json.dumps(MOCK_REQUIREMENTS)
    mock_model.generate_content.return_value = mock_resp

    result = extract_jd_requirements("We are looking for a Senior Product Manager with 5+ years of experience in product management, preferably in fintech or SaaS. The candidate should have experience working with cross-functional teams,stakeholder management, roadmap planning, and data-driven decision making.",
                                     "product manager", "Senior Product Manager")
    assert result["min_years_experience"] == 5
    assert "fintech" in result["domains"]
    assert result["role_is_match"] is True

@patch("modules.jd_analyzer.model")
def test_extract_strips_markdown_fences(mock_model):
    mock_resp = MagicMock()
    mock_resp.text = "```json\n" + json.dumps(MOCK_REQUIREMENTS) + "\n```"
    mock_model.generate_content.return_value = mock_resp

    result = extract_jd_requirements("We are looking for a Senior Product Manager with 5+ years of experience in product management, preferably in fintech or SaaS. The candidate should have experience working with cross-functional teams,stakeholder management, roadmap planning, and data-driven decision making.",
                                     "product manager", "PM")
    assert result["min_years_experience"] == 5

def test_extract_short_jd_returns_defaults():
    """Short JD should skip LLM and return safe defaults — no API call made."""
    result = extract_jd_requirements("PM role", "product manager", "PM")
    assert result["role_is_match"] is True
    assert result["min_years_experience"] is None

@patch("modules.jd_analyzer.extract_jd_requirements", return_value=MOCK_REQUIREMENTS)
def test_analyze_match_good_fit(mock_extract):
    job = {"job_id": "1", "title": "Senior PM", "company": "Razorpay",
           "location": "Bangalore", "description": "long enough jd text here",
           "link": "#", "date": "2026-04-25"}
    result = analyze_match(job, years_exp=6, search_role="product manager", domain="fintech")

    assert result["score"] >= 70
    assert result["is_role_match"] is True
    assert any("Experience OK" in r for r in result["reasons"])
    assert any("Domain match" in r for r in result["reasons"])

@patch("modules.jd_analyzer.extract_jd_requirements", return_value={
    **MOCK_REQUIREMENTS, "min_years_experience": 8
})
def test_analyze_match_underqualified(mock_extract):
    job = {"job_id": "2", "title": "Senior PM", "company": "X",
           "location": "Remote", "description": "long jd text here for testing",
           "link": "#", "date": "2026-04-25"}
    result = analyze_match(job, years_exp=3, search_role="product manager")
    assert result["score"] < 50
    assert any("under" in w.lower() for w in result["warnings"])

@patch("modules.jd_analyzer.extract_jd_requirements", return_value={
    **MOCK_REQUIREMENTS,
    "role_is_match": False,
    "role_match_reason": "Project manager is a different discipline"
})
def test_analyze_match_role_mismatch_scores_zero(mock_extract):
    job = {"job_id": "3", "title": "Project Manager", "company": "X",
           "location": "Remote", "description": "long jd text here for testing",
           "link": "#", "date": "2026-04-25"}
    result = analyze_match(job, years_exp=6, search_role="product manager")
    assert result["score"] == 0
    assert result["is_role_match"] is False
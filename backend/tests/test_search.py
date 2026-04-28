import pytest
from unittest.mock import patch, MagicMock
from modules.search import fetch_jobs, _parse_search_results, get_experience_codes

# Minimal HTML fragment matching LinkedIn guest API response format
MOCK_HTML = """
<div class="job-search-card" data-entity-urn="urn:li:jobPosting:111222333">
  <a class="base-card__full-link" href="https://in.linkedin.com/jobs/view/pm-at-flipkart-111222333?refId=xyz"></a>
  <h3 class="base-search-card__title">Senior Product Manager</h3>
  <h4 class="base-search-card__subtitle">Flipkart</h4>
  <span class="job-search-card__location">Bengaluru, Karnataka, India</span>
  <time class="job-search-card__listdate--new" datetime="2026-04-25">3 days ago</time>
</div>
"""

def test_get_experience_codes():
    assert get_experience_codes(1)  == "1,2"
    assert get_experience_codes(2)  == "1,2"
    assert get_experience_codes(3)  == "2,3"
    assert get_experience_codes(5)  == "2,3"
    assert get_experience_codes(6)  == "3,4"
    assert get_experience_codes(10) == "3,4"
    assert get_experience_codes(11) == "4,5,6"

def test_parse_search_results_success():
    jobs = _parse_search_results(MOCK_HTML)
    assert len(jobs) == 1
    j = jobs[0]
    assert j["job_id"] == "111222333"
    assert j["title"] == "Senior Product Manager"
    assert j["company"] == "Flipkart"
    assert "Bengaluru" in j["location"]
    assert j["link"] == "https://in.linkedin.com/jobs/view/pm-at-flipkart-111222333"
    assert j["date"] == "2026-04-25"
    assert j["description"] == ""   # not fetched yet

def test_parse_search_results_empty_html():
    jobs = _parse_search_results("<html><body>No jobs here</body></html>")
    assert jobs == []

def test_parse_search_results_missing_fields():
    """Cards with no URN should be skipped gracefully."""
    html = '<div class="job-search-card"><h3 class="base-search-card__title">Some Job</h3></div>'
    jobs = _parse_search_results(html)
    assert jobs == []

@patch("modules.search.requests.get")
def test_fetch_jobs_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = MOCK_HTML
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp

    jobs = fetch_jobs("Product Manager", location="India",
                      time_filter="24h", years_exp=6, limit=1)
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Senior Product Manager"

@patch("modules.search.requests.get")
def test_fetch_jobs_stops_on_400(mock_get):
    """LinkedIn returns 400 when no more pages — should stop cleanly."""
    mock_resp = MagicMock()
    mock_resp.status_code = 400
    mock_get.return_value = mock_resp

    jobs = fetch_jobs("Product Manager", limit=10)
    assert jobs == []

@patch("modules.search.requests.get")
def test_fetch_job_description(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = """
    <div class="description__text">
      <section><div>We need 5+ years of PM experience in fintech.</div></section>
    </div>"""
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp

    from modules.search import fetch_job_description
    job = {"job_id": "123", "title": "PM", "company": "Test", "description": ""}
    result = fetch_job_description(job)
    assert len(result["description"]) > 0
    assert "5+" in result["description"]
import pytest
from unittest.mock import patch, MagicMock, call
from modules.scheduler import set_schedule, INTERVAL_MAP

USER_CONFIG = {
    "role": "Product Manager",
    "location": "India",
    "time_filter": "24h",
    "years_exp": 6,
    "domain": "fintech",
    "notify_email": "test@example.com",
}

def test_interval_map_values():
    assert INTERVAL_MAP["15m"] == 15
    assert INTERVAL_MAP["1h"]  == 60
    assert INTERVAL_MAP["3h"]  == 180

@patch("modules.scheduler.scheduler")
def test_set_schedule_adds_job(mock_scheduler):
    set_schedule("1h", USER_CONFIG)
    mock_scheduler.remove_all_jobs.assert_called_once()
    mock_scheduler.add_job.assert_called_once()

@patch("modules.scheduler.scheduler")
def test_set_schedule_removes_old_jobs_first(mock_scheduler):
    """Changing schedule should clear previous jobs first."""
    set_schedule("15m", USER_CONFIG)
    set_schedule("3h", USER_CONFIG)
    assert mock_scheduler.remove_all_jobs.call_count == 2

@patch("modules.scheduler.send_jobs_email")
@patch("modules.scheduler.mark_as_sent")
@patch("modules.scheduler.filter_new_jobs", return_value=[
    {"job_id": "1", "title": "PM", "company": "X",
     "location": "Blr", "link": "#", "description": "...",
     "match": {"score": 80, "is_role_match": True}}
])
@patch("modules.scheduler.analyze_match", return_value={
    "score": 80, "is_role_match": True, "reasons": [], "warnings": [],
    "job": {"job_id": "1", "title": "PM", "company": "X",
            "location": "Blr", "link": "#", "description": "..."}
})
@patch("modules.scheduler.fetch_jobs", return_value=[
    {"job_id": "1", "title": "PM", "company": "X",
     "location": "Blr", "link": "#", "description": "long jd text here"}
])
def test_run_job_search_full_pipeline(mock_fetch, mock_analyze,
                                       mock_filter, mock_mark, mock_email):
    from modules.scheduler import run_job_search
    run_job_search(USER_CONFIG)

    mock_fetch.assert_called_once()
    mock_analyze.assert_called_once()
    mock_email.assert_called_once_with(mock_filter.return_value,
                                        USER_CONFIG["notify_email"])
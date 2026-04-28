import pytest
from unittest.mock import patch, MagicMock
from modules.dedup import is_already_sent, mark_as_sent, filter_new_jobs

JOBS = [
    {"job_id": "aaa", "title": "PM", "company": "A"},
    {"job_id": "bbb", "title": "Senior PM", "company": "B"},
    {"job_id": "ccc", "title": "APM", "company": "C"},
]

@patch("modules.dedup.SessionLocal")
def test_is_already_sent_true(mock_session_cls):
    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = MagicMock()  # found
    mock_session_cls.return_value = mock_db

    assert is_already_sent("aaa") is True

@patch("modules.dedup.SessionLocal")
def test_is_already_sent_false(mock_session_cls):
    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = None  # not found
    mock_session_cls.return_value = mock_db

    assert is_already_sent("zzz") is False

@patch("modules.dedup.SessionLocal")
def test_mark_as_sent(mock_session_cls):
    mock_db = MagicMock()
    mock_session_cls.return_value = mock_db

    mark_as_sent("aaa", "PM", "CompanyA")

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

@patch("modules.dedup.is_already_sent", side_effect=lambda job_id: job_id == "aaa")
def test_filter_new_jobs(mock_check):
    """'aaa' already sent, 'bbb' and 'ccc' are new."""
    new = filter_new_jobs(JOBS)
    assert len(new) == 2
    assert all(j["job_id"] != "aaa" for j in new)

@patch("modules.dedup.is_already_sent", return_value=True)
def test_filter_new_jobs_all_sent(mock_check):
    new = filter_new_jobs(JOBS)
    assert new == []
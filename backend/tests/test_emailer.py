import pytest
from unittest.mock import patch, MagicMock
from email import message_from_string
from modules.emailer import send_jobs_email

JOBS = [
    {
        "job_id": "1",
        "title": "Senior PM",
        "company": "Flipkart",
        "location": "Bangalore",
        "link": "https://linkedin.com/jobs/1",
        "match": {"score": 85},
    },
    {
        "job_id": "2",
        "title": "APM",
        "company": "Razorpay",
        "location": "Mumbai",
        "link": "https://linkedin.com/jobs/2",
        "match": {"score": 70},
    },
]


@patch("modules.emailer.smtplib.SMTP_SSL")
def test_send_jobs_email_success(mock_smtp_cls):
    mock_server = MagicMock()
    mock_smtp_cls.return_value.__enter__.return_value = mock_server

    send_jobs_email(JOBS, "riturajbanerjee.1999.rb@gmail.com")

    mock_server.login.assert_called_once()
    mock_server.sendmail.assert_called_once()

    args = mock_server.sendmail.call_args[0]
    assert args[1] == "riturajbanerjee.1999.rb@gmail.com"


@patch("modules.emailer.smtplib.SMTP_SSL")
def test_send_jobs_email_empty_list(mock_smtp_cls):
    """Empty list should not attempt to send anything."""
    send_jobs_email([], "riturajbanerjee.1999.rb@gmail.com")

    mock_smtp_cls.assert_not_called()


@patch("modules.emailer.smtplib.SMTP_SSL")
def test_email_body_contains_job_titles(mock_smtp_cls):
    mock_server = MagicMock()
    mock_smtp_cls.return_value.__enter__.return_value = mock_server

    send_jobs_email(JOBS, "riturajbanerjee.1999.rb@gmail.com")

    # Raw MIME message
    sent_message = mock_server.sendmail.call_args[0][2]

    # Parse MIME message
    msg = message_from_string(sent_message)

    # Decode HTML body from MIME payload
    if msg.is_multipart():
        payload = msg.get_payload()[0].get_payload(decode=True).decode("utf-8")
    else:
        payload = msg.get_payload(decode=True).decode("utf-8")

    assert "Senior PM" in payload
    assert "Flipkart" in payload
    assert "85" in payload  # match score


@patch("modules.emailer.smtplib.SMTP_SSL")
def test_email_raises_on_smtp_failure(mock_smtp_cls):
    mock_smtp_cls.side_effect = Exception("SMTP connection refused")

    with pytest.raises(Exception, match="SMTP connection refused"):
        send_jobs_email(JOBS, "riturajbanerjee.1999.rb@gmail.com")
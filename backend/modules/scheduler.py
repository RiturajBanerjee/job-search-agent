import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from modules.search import fetch_jobs
from modules.jd_analyzer import analyze_match
from modules.dedup import filter_new_jobs, mark_as_sent
from modules.emailer import send_jobs_email

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()

def run_job_search(user_config: dict):


    logger.info(f"Running scheduled search for config: {user_config}")
    jobs = fetch_jobs(
        role=user_config["role"],
        location=user_config.get("location", "India"),
        time_filter=user_config["time_filter"],
        years_exp=user_config.get("years_exp", 5),
    )
    analyzed = [
        analyze_match(
            j,
            years_exp=user_config["years_exp"],
            search_role=user_config["role"],      # ← pass the role
            domain=user_config.get("domain")
        )
        for j in jobs
    ]
    analyzed = [a for a in analyzed if a["is_role_match"] and a["score"] >= 30]  # filter weak matches
    new_jobs = filter_new_jobs([a["job"] | {"match": a} for a in analyzed])

    for j in new_jobs:
        mark_as_sent(j["job_id"], j["title"], j["company"])

    send_jobs_email(new_jobs, user_config["notify_email"])

INTERVAL_MAP = {"15m": 15, "1h": 60, "3h": 180}

def set_schedule(interval_key: str, user_config: dict):
    scheduler.remove_all_jobs()
    minutes = INTERVAL_MAP.get(interval_key, 60)
    scheduler.add_job(run_job_search, IntervalTrigger(minutes=minutes), args=[user_config])
    logger.info(f"Scheduler set to every {minutes} minutes")

def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")
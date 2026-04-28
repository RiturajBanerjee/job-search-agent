# backend/modules/search.py
import requests
import logging
import time
from bs4 import BeautifulSoup
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

TIME_FILTER_MAP = {
    "24h": "r86400",
    "1w":  "r604800",
    "1m":  "r2592000",
}

# Map years of experience to LinkedIn f_E codes
# LinkedIn codes: 1=Internship 2=Entry 3=Associate 4=Mid-Senior 5=Director 6=Executive
def get_experience_codes(years: int) -> str:
    if years <= 2:
        return "1,2"       # Internship + Entry level
    elif years <= 5:
        return "2,3"       # Entry + Associate
    elif years <= 10:
        return "3,4"       # Associate + Mid-Senior
    else:
        return "4,5,6"     # Mid-Senior + Director + Executive

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# LinkedIn guest API — returns HTML fragments, 10 jobs per page
SEARCH_API = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

# LinkedIn job detail API — returns full JD HTML for one job
JOB_DETAIL_API = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"


def fetch_jobs(role: str, location: str = "India", time_filter: str = "24h",
               years_exp: int = 5, limit: int = 20) -> list:
    """
    Fetch jobs from LinkedIn guest API with experience level pre-filtering.
    Uses f_E parameter so LinkedIn filters by seniority BEFORE we receive results.
    """
    time_code = TIME_FILTER_MAP.get(time_filter, "r86400")
    exp_codes = get_experience_codes(years_exp)

    logger.info(
        f"Searching LinkedIn | role='{role}' | location='{location}' | "
        f"time={time_filter} | years_exp={years_exp} → f_E={exp_codes}"
    )

    all_jobs = []
    start = 0

    while len(all_jobs) < limit:
        params = {
            "keywords":  role,
            "location":  location,
            "f_TPR":     time_code,
            "f_E":       exp_codes,
            "f_JT":      "F",        # Full-time only
            "sortBy":    "DD",       # Most recent first
            "start":     start,
        }

        try:
            query_string = urlencode({k: v for k, v in params.items() if k != "f_E"})
            url = f"{SEARCH_API}?{query_string}&f_E={exp_codes}"
            response = requests.get(url, headers=HEADERS, timeout=15)

            # 400 means no more results (LinkedIn returns 400 at end of pagination)
            if response.status_code == 400:
                logger.info("LinkedIn returned 400 — no more results")
                break

            response.raise_for_status()

            jobs_batch = _parse_search_results(response.text)
            if not jobs_batch:
                logger.info("No job cards in response, stopping")
                break

            all_jobs.extend(jobs_batch)
            logger.info(f"Page start={start}: got {len(jobs_batch)} jobs (total: {len(all_jobs)})")

            start += 10   # guest API paginates in 10s
            time.sleep(2) # polite delay

        except requests.HTTPError as e:
            if e.response.status_code == 429:
                logger.warning("Rate limited — waiting 15s")
                time.sleep(15)
            else:
                logger.error(f"HTTP {e.response.status_code}")
            break
        except requests.RequestException as e:
            logger.error(f"Request error: {e}")
            break

    result = all_jobs[:limit]
    logger.info(f"Returning {len(result)} jobs for '{role}'")
    return result


def _parse_search_results(html: str) -> list:
    """Parse LinkedIn guest API HTML fragment — returns list of job dicts."""
    soup = BeautifulSoup(html, "lxml")
    jobs = []

    # Guest API returns <div class="base-card ... job-search-card">
    cards = soup.find_all("div", class_="job-search-card")

    for card in cards:
        try:
            # Job ID from data-entity-urn="urn:li:jobPosting:1234567"
            urn = card.get("data-entity-urn", "")
            job_id = urn.split(":")[-1] if urn else ""
            if not job_id:
                continue

            # Title — [class*=_title] or h3.base-search-card__title
            title_tag = card.find(class_=lambda c: c and "_title" in c) or \
                        card.find("h3", class_="base-search-card__title")
            title = title_tag.get_text(strip=True) if title_tag else ""

            # Link — [class*=_full-link]
            link_tag = card.find(class_=lambda c: c and "_full-link" in c)
            link = link_tag.get("href", "").split("?")[0] if link_tag else ""

            # Company — [class*=_subtitle]
            company_tag = card.find(class_=lambda c: c and "_subtitle" in c)
            company = company_tag.get_text(strip=True) if company_tag else ""

            # Location — [class*=_location]
            location_tag = card.find(class_=lambda c: c and "_location" in c)
            location = location_tag.get_text(strip=True) if location_tag else ""

            # Date — [class*=listdate]
            date_tag = card.find(class_=lambda c: c and "listdate" in c)
            date = date_tag.get("datetime", "") if date_tag else ""

            jobs.append({
                "job_id":      job_id,
                "title":       title,
                "company":     company,
                "location":    location,
                "description": "",   # filled by fetch_job_description()
                "link":        link,
                "date":        date,
                "is_remote":   "remote" in location.lower(),
                "source":      "linkedin",
            })
            logger.info(f"  Parsed: {title} @ {company} [{location}]")

        except Exception as e:
            logger.warning(f"Failed to parse card: {e}")
            continue

    return jobs


def fetch_job_description(job: dict) -> dict:
    """
    Fetch full JD using LinkedIn's job detail guest API.
    Much more reliable than scraping the full job page.
    URL: https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}
    """
    job_id = job.get("job_id", "")
    if not job_id:
        logger.warning("No job_id, cannot fetch description")
        return job

    url = JOB_DETAIL_API.format(job_id=job_id)

    try:
        logger.info(f"Fetching JD via API: {job.get('title')} @ {job.get('company')}")
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        # Job detail API returns description inside [class*=description] > section > div
        desc_tag = soup.find(class_=lambda c: c and "description" in c)
        if desc_tag:
            # Dig into section > div if present
            inner = desc_tag.find("div") or desc_tag
            job["description"] = inner.get_text(separator=" ", strip=True)
            logger.info(f"Got JD: {len(job['description'])} chars")
        else:
            logger.warning(f"No description found for job {job_id}")

        time.sleep(1)

    except requests.RequestException as e:
        logger.error(f"Failed to fetch JD for {job_id}: {e}")

    return job
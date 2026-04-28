job-search-agent/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # App settings / env vars
│   ├── database.py          # DB setup (SQLAlchemy)
│   ├── models.py            # DB models
│   ├── auth.py              # Login / JWT
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── search.py        # LinkedIn job scraper
│   │   ├── jd_analyzer.py   # JD vs experience matcher
│   │   ├── dedup.py         # Already-sent job tracker
│   │   ├── emailer.py       # Send email
│   │   └── scheduler.py     # APScheduler setup
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth_router.py
│   │   ├── config_router.py
│   │   └── jobs_router.py
│   ├── tests/               # One test file per module
│   │   ├── test_search.py
│   │   ├── test_jd_analyzer.py
│   │   ├── test_dedup.py
│   │   ├── test_emailer.py
│   │   └── test_scheduler.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   └── Settings.jsx
│   │   └── api.js           # Axios API client
│   ├── package.json
│   └── .env.example
├── render.yaml              # Render deployment config
├── .github/
│   └── workflows/
│       └── test.yml         # Auto-run tests on push
└── README.md
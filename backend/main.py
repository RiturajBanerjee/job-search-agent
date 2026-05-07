# backend/main.py
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from modules.scheduler import start_scheduler
from routers.auth_router import router as auth_router
from routers.jobs_router import router as jobs_router
from routers.config_router import router as config_router

# Logging setup — all modules use this
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once on startup
    logger.info("Starting JobRadar backend...")
    init_db()           # create tables if they don't exist
    start_scheduler()   # start the background job scheduler
    logger.info("Backend ready ✓")
    yield
    # Runs on shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title="JobRadar API",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow requests from React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # React dev
        "http://localhost:5173",   # Vite dev (if used)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all routers
app.include_router(auth_router)
app.include_router(jobs_router)
app.include_router(config_router)

@app.get("/health")
def health():
    return {"status": "ok"}
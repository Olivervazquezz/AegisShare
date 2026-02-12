"""
AegisShare — FastAPI Application

Main module that bootstraps the app, registers routers,
and configures CORS.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import database, models
from .routers import auth, scan, history, stats, policies, users

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="AegisShare",
    description="AI-Powered Data Loss Prevention platform.",
    version="2.0.0",
)

# ---------------------------------------------------------------------------
# CORS — allow the React dev server during development
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth.router)
app.include_router(scan.router)
app.include_router(history.router)
app.include_router(stats.router)
app.include_router(policies.router)
app.include_router(users.router)
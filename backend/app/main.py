from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db import ping
from app.routers import accounts_runs, agent_activity, auth, forecasts_savings, recommendations, resources


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield  # nothing to do on shutdown for the demo


settings = get_settings()

app = FastAPI(
    title="CloudCare API",
    description="AI-Powered Cloud Cost Optimization & Resource Intelligence Platform — backend API.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(resources.router)
app.include_router(agent_activity.router)
app.include_router(recommendations.router)
app.include_router(forecasts_savings.router)
app.include_router(accounts_runs.router)


@app.get("/")
async def root() -> dict:
    return {"service": "cloudcare-api", "status": "ok"}


@app.get("/health")
async def health() -> dict:
    """
    Returns mongo_connected: false until you set a real MONGODB_URI in
    backend/.env — that's expected out of the box, not a bug.
    """
    return {"status": "ok", "mongo_connected": await ping()}

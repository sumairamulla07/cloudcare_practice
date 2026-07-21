from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers import (
    accounts_runs,
    agent_activity,
    auth,
    forecasts_savings,
    recommendations,
    resources,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

settings = get_settings()

app = FastAPI(
    title="CloudCare API",
    description="AI-Powered Cloud Cost Optimization & Resource Intelligence Platform backend API.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
    ],
)


app.include_router(auth.router)
app.include_router(resources.router)
app.include_router(agent_activity.router)
app.include_router(recommendations.router)
app.include_router(forecasts_savings.router)
app.include_router(accounts_runs.router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "cloudcare-api",
        "status": "ok",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "cloudcare-api",
    }

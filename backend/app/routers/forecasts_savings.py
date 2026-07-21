from fastapi import APIRouter

from app.mock_data import FORECAST, SAVINGS_SUMMARY
from app.models.schemas import ForecastPoint, SavingsSummary

router = APIRouter(prefix="/v1", tags=["forecasts-savings"])


@router.get("/forecasts", response_model=list[ForecastPoint])
async def get_forecast() -> list[ForecastPoint]:
    """
    TODO: replace with the real forecasting pipeline (blueprint 5.2) —
    aggregate daily CostRecord documents from Mongo, run select_forecast()
    from services/forecasting, and return prediction intervals.
    """
    return FORECAST


@router.get("/savings", response_model=SavingsSummary)
async def get_savings_summary() -> SavingsSummary:
    """
    TODO: compute this from verified Feedback documents (blueprint 4.1)
    instead of returning a hardcoded summary — baseline cost minus
    post-action normalized cost, summed per tenant/account.
    """
    return SAVINGS_SUMMARY

"""
Forecasting service — blueprint §5.2.

Public API:
    from app.services.forecasting import select_forecast
"""

from app.services.forecasting.select import select_forecast

__all__ = ["select_forecast"]

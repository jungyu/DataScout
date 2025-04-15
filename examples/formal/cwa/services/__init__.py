"""
中央氣象局 API 服務模組
"""

from .earthquake import EarthquakeService
from .rainfall import RainfallService
from .typhoon import TyphoonService
from .forecast import ForecastService
from .observation import ObservationService
from .township_forecast import TownshipForecastService

__all__ = ["EarthquakeService", "RainfallService", "TyphoonService", "ForecastService", "ObservationService", "TownshipForecastService"] 
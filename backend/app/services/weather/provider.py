from abc import ABC, abstractmethod
from datetime import datetime

from app.services.weather.base import WeatherData


class WeatherProvider(ABC):

    @abstractmethod
    def get_current_weather(
        self,
        latitude: float,
        longitude: float,
    ) -> WeatherData:
        raise NotImplementedError

    @abstractmethod
    def get_forecast(
        self,
        latitude: float,
        longitude: float,
        start_at: datetime,
        end_at: datetime,
    ) -> list[WeatherData]:
        raise NotImplementedError
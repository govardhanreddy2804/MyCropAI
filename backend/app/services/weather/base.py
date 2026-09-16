from dataclasses import dataclass
from datetime import datetime


@dataclass
class WeatherData:
    observed_at: datetime

    air_temperature: float | None = None
    air_humidity: float | None = None
    rainfall: float | None = None
    wind_speed: float | None = None

    temperature_unit: str = "celsius"
    humidity_unit: str = "percent"
    rainfall_unit: str = "mm"
    wind_speed_unit: str = "m/s"
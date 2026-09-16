from app.core.config import settings
from app.services.weather.openweather import OpenWeatherProvider
from app.services.weather.provider import WeatherProvider


def get_weather_provider() -> WeatherProvider:
    if settings.weather_provider == "openweather":
        return OpenWeatherProvider()

    raise RuntimeError(
        f"Unsupported weather provider: {settings.weather_provider}"
    )
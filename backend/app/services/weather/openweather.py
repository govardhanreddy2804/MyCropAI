from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.services.weather.base import WeatherData
from app.services.weather.provider import WeatherProvider


class OpenWeatherProvider(WeatherProvider):
    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.weather_api_key

    def _require_api_key(self) -> str:
        if not self.api_key:
            raise RuntimeError("Weather API key is not configured")
        return self.api_key

    def get_current_weather(
        self,
        latitude: float,
        longitude: float,
    ) -> WeatherData:
        api_key = self._require_api_key()

        response = httpx.get(
            f"{self.BASE_URL}/weather",
            params={
                "lat": latitude,
                "lon": longitude,
                "appid": api_key,
                "units": "metric",
            },
            timeout=10.0,
        )

        response.raise_for_status()
        data = response.json()

        observed_at = datetime.fromtimestamp(
            data["dt"],
            tz=timezone.utc,
        )

        return WeatherData(
            observed_at=observed_at,
            air_temperature=data["main"]["temp"],
            air_humidity=data["main"]["humidity"],
            rainfall=(
                data.get("rain", {}).get("1h")
                or data.get("rain", {}).get("3h")
            ),
            wind_speed=data.get("wind", {}).get("speed"),
        )

    def get_forecast(
        self,
        latitude: float,
        longitude: float,
        start_at: datetime,
        end_at: datetime,
    ) -> list[WeatherData]:
        api_key = self._require_api_key()

        response = httpx.get(
            f"{self.BASE_URL}/forecast",
            params={
                "lat": latitude,
                "lon": longitude,
                "appid": api_key,
                "units": "metric",
            },
            timeout=10.0,
        )

        response.raise_for_status()
        data = response.json()

        results: list[WeatherData] = []

        for item in data.get("list", []):
            observed_at = datetime.fromtimestamp(
                item["dt"],
                tz=timezone.utc,
            )

            if start_at <= observed_at <= end_at:
                results.append(
                    WeatherData(
                        observed_at=observed_at,
                        air_temperature=item["main"]["temp"],
                        air_humidity=item["main"]["humidity"],
                        rainfall=(
                            item.get("rain", {}).get("3h")
                        ),
                        wind_speed=item.get("wind", {}).get("speed"),
                    )
                )

        return results
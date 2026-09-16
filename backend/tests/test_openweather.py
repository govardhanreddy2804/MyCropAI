def test_openweather_provider_normalizes_response(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "dt": 1750000000,
                "main": {
                    "temp": 30.5,
                    "humidity": 72,
                },
                "wind": {
                    "speed": 3.5,
                },
                "rain": {
                    "1h": 1.2,
                },
            }

    def fake_get(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(
        "app.services.weather.openweather.httpx.get",
        fake_get,
    )

    from app.services.weather.openweather import OpenWeatherProvider

    provider = OpenWeatherProvider(
        api_key="test-key",
    )

    weather = provider.get_current_weather(
        latitude=17.385,
        longitude=78.4867,
    )

    assert weather.air_temperature == 30.5
    assert weather.air_humidity == 72
    assert weather.rainfall == 1.2
    assert weather.wind_speed == 3.5
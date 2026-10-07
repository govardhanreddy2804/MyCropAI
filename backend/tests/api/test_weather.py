from tests.api.test_observations import create_test_farm_and_field


def test_weather_requires_field_coordinates(
    authenticated_client,
):
    farm, field = create_test_farm_and_field(authenticated_client)

    response = authenticated_client.post(
        f"/api/v1/farms/{farm['id']}/fields/{field['id']}/weather/current"
    )

    assert response.status_code == 400
    assert "coordinates" in response.json()["detail"].lower()


def test_weather_sync_accepts_background_task(
    authenticated_client,
    farm,
    field_with_coordinates,
):
    response = authenticated_client.post(
        f"/api/v1/farms/{farm.id}/fields/{field_with_coordinates.id}/weather/sync"
    )

    assert response.status_code == 202

    data = response.json()

    assert data["accepted"] is True
    assert "accepted" in data["message"].lower()

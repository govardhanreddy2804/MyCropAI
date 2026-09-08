from datetime import datetime, timezone
from uuid import uuid4


def create_test_farm_and_field(authenticated_client):
    farm_response = authenticated_client.post(
        "/api/v1/farms",
        json={
            "name": "Observation Farm",
            "location": "Karnataka",
            "area": 5,
        },
    )

    assert farm_response.status_code == 201

    farm = farm_response.json()

    field_response = authenticated_client.post(
        f"/api/v1/farms/{farm['id']}/fields",
        json={
            "name": "Observation Field",
            "area": 2,
        },
    )

    assert field_response.status_code == 201

    return farm, field_response.json()


def test_create_manual_observation(
    authenticated_client,
):
    farm, field = create_test_farm_and_field(
        authenticated_client
    )

    response = authenticated_client.post(
        f"/api/v1/farms/{farm['id']}/fields/{field['id']}/observations",
        json={
            "observation_type": "soil_moisture",
            "value": 28.5,
            "unit": "%",
            "source": "manual",
            "observed_at": "2026-09-07T10:30:00Z",
            "confidence": 0.9,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["field_id"] == field["id"]
    assert data["observation_type"] == "soil_moisture"
    assert data["value"] == 28.5
    assert data["unit"] == "%"
    assert data["source"] == "manual"
    assert data["confidence"] == 0.9


def test_list_field_observations(
    authenticated_client,
):
    farm, field = create_test_farm_and_field(
        authenticated_client
    )

    for observation in [
        {
            "observation_type": "soil_moisture",
            "value": 25,
            "unit": "%",
            "source": "manual",
            "observed_at": "2026-09-07T09:00:00Z",
        },
        {
            "observation_type": "air_humidity",
            "value": 65,
            "unit": "%",
            "source": "weather_api",
            "observed_at": "2026-09-07T10:00:00Z",
        },
    ]:
        response = authenticated_client.post(
            f"/api/v1/farms/{farm['id']}/fields/{field['id']}/observations",
            json=observation,
        )

        assert response.status_code == 201

    response = authenticated_client.get(
        f"/api/v1/farms/{farm['id']}/fields/{field['id']}/observations"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["observation_type"] == "air_humidity"
    assert data[1]["observation_type"] == "soil_moisture"


def test_delete_observation(
    authenticated_client,
):
    farm, field = create_test_farm_and_field(
        authenticated_client
    )

    create_response = authenticated_client.post(
        f"/api/v1/farms/{farm['id']}/fields/{field['id']}/observations",
        json={
            "observation_type": "soil_ph",
            "value": 6.8,
            "unit": "pH",
            "source": "manual",
            "observed_at": "2026-09-07T10:00:00Z",
        },
    )

    assert create_response.status_code == 201

    observation = create_response.json()

    delete_response = authenticated_client.delete(
        f"/api/v1/farms/{farm['id']}/fields/{field['id']}/observations/{observation['id']}"
    )

    assert delete_response.status_code == 204

    list_response = authenticated_client.get(
        f"/api/v1/farms/{farm['id']}/fields/{field['id']}/observations"
    )

    assert list_response.status_code == 200
    assert list_response.json() == []


def test_farmer_cannot_access_another_farm_observations(
    authenticated_client,
    second_authenticated_client,
):
    farm, field = create_test_farm_and_field(
        authenticated_client
    )

    response = second_authenticated_client.get(
        f"/api/v1/farms/{farm['id']}/fields/{field['id']}/observations"
    )

    assert response.status_code == 403


def test_observation_cannot_be_added_to_another_farm_field(
    authenticated_client,
    second_authenticated_client,
):
    farm, field = create_test_farm_and_field(
        authenticated_client
    )

    response = second_authenticated_client.post(
        f"/api/v1/farms/{farm['id']}/fields/{field['id']}/observations",
        json={
            "observation_type": "soil_moisture",
            "value": 30,
            "unit": "%",
            "source": "manual",
            "observed_at": "2026-09-07T10:00:00Z",
        },
    )

    assert response.status_code == 403


def test_missing_observation_returns_404(
    authenticated_client,
):
    farm, field = create_test_farm_and_field(
        authenticated_client
    )

    observation_id = uuid4()

    response = authenticated_client.delete(
        f"/api/v1/farms/{farm['id']}/fields/{field['id']}/observations/{observation_id}"
    )

    assert response.status_code == 404
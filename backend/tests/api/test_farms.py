from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException


from app.models.enums import UserRole
from app.policies.farm_policy import (
    can_access_farm,
    require_farm_access,
)


def make_user(role, user_id=None):
    return SimpleNamespace(
        id=user_id or uuid4(),
        role=role,
    )


def make_farm(owner_id):
    return SimpleNamespace(
        id=uuid4(),
        owner_id=owner_id,
    )


def test_admin_can_access_any_farm():
    admin = make_user(UserRole.ADMIN)
    farm = make_farm(uuid4())

    assert can_access_farm(admin, farm) is True


def test_farmer_can_access_own_farm():
    farmer_id = uuid4()

    farmer = make_user(
        UserRole.FARMER,
        farmer_id,
    )

    farm = make_farm(farmer_id)

    assert can_access_farm(farmer, farm) is True


def test_farmer_cannot_access_other_farm():
    farmer = make_user(UserRole.FARMER)

    farm = make_farm(uuid4())

    assert can_access_farm(farmer, farm) is False


def test_require_farm_access_returns_farm():
    farmer_id = uuid4()

    farmer = make_user(
        UserRole.FARMER,
        farmer_id,
    )

    farm = make_farm(farmer_id)

    result = require_farm_access(
        farmer,
        farm,
    )

    assert result is farm


def test_require_farm_access_raises_403():
    farmer = make_user(UserRole.FARMER)

    farm = make_farm(uuid4())

    with pytest.raises(HTTPException) as exc_info:
        require_farm_access(
            farmer,
            farm,
        )

    assert exc_info.value.status_code == 403


def test_list_farms_requires_authentication(
    client,
):
    response = client.get(
        "/api/v1/farms"
    )

    assert response.status_code == 401


def test_create_farm(
    authenticated_client,
):
    response = authenticated_client.post(
        "/api/v1/farms",
        json={
            "name": "Green Valley",
            "location": "Karnataka",
            "area": 5.5,
            "soil_type": "Loamy",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Green Valley"
    assert data["area"] == 5.5

    assert data["owner_id"] == str(
        authenticated_client.user.id
    )

def test_create_farm_cannot_set_owner_id(
    authenticated_client,
):
    fake_owner_id = str(uuid4())

    response = authenticated_client.post(
        "/api/v1/farms",
        json={
            "name": "Malicious Farm",
            "location": "Unknown",
            "area": 5,
            "soil_type": "Clay",
            "owner_id": fake_owner_id,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["owner_id"] == str(
        authenticated_client.user.id
    )

    assert data["owner_id"] != fake_owner_id

def test_update_own_farm(
    authenticated_client,
):
    create_response = authenticated_client.post(
        "/api/v1/farms",
        json={
            "name": "Original Farm",
            "location": "Karnataka",
            "area": 5,
            "soil_type": "Loamy",
        },
    )

    assert create_response.status_code == 201

    farm = create_response.json()

    response = authenticated_client.client.put(
        f"/api/v1/farms/{farm['id']}",
        json={
            "name": "Updated Farm",
            "area": 7.5,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Updated Farm"
    assert data["area"] == 7.5
    assert data["location"] == "Karnataka"
    assert data["soil_type"] == "Loamy"


def test_update_missing_farm(
    authenticated_client,
):
    farm_id = uuid4()

    response = authenticated_client.client.put(
        f"/api/v1/farms/{farm_id}",
        json={
            "name": "Updated Farm",
        },
    )

    assert response.status_code == 404


def test_delete_own_farm(
    authenticated_client,
):
    create_response = authenticated_client.post(
        "/api/v1/farms",
        json={
            "name": "Farm To Delete",
            "location": "Karnataka",
            "area": 5,
            "soil_type": "Loamy",
        },
    )

    assert create_response.status_code == 201

    farm = create_response.json()

    delete_response = authenticated_client.client.delete(
        f"/api/v1/farms/{farm['id']}"
    )

    assert delete_response.status_code == 204

    get_response = authenticated_client.client.get(
        f"/api/v1/farms/{farm['id']}"
    )

    assert get_response.status_code == 404


def test_delete_missing_farm(
    authenticated_client,
):
    farm_id = uuid4()

    response = authenticated_client.client.delete(
        f"/api/v1/farms/{farm_id}"
    )

    assert response.status_code == 404

def test_farmer_cannot_update_another_farm(
    authenticated_client,
    second_authenticated_client,
):
    create_response = authenticated_client.post(
        "/api/v1/farms",
        json={
            "name": "Farmer A Farm",
            "location": "Karnataka",
            "area": 5,
            "soil_type": "Loamy",
        },
    )

    assert create_response.status_code == 201

    farm = create_response.json()

    response = second_authenticated_client.put(
        f"/api/v1/farms/{farm['id']}",
        json={
            "name": "Hacked Farm",
        },
    )

    assert response.status_code == 403

def test_farmer_cannot_delete_another_farm(
    authenticated_client,
    second_authenticated_client,
):
    create_response = authenticated_client.post(
        "/api/v1/farms",
        json={
            "name": "Farmer A Farm",
            "location": "Karnataka",
            "area": 5,
            "soil_type": "Loamy",
        },
    )

    assert create_response.status_code == 201

    farm = create_response.json()

    response = second_authenticated_client.delete(
        f"/api/v1/farms/{farm['id']}"
    )

    assert response.status_code == 403

def test_create_field(
    authenticated_client,
):
    farm_response = authenticated_client.post(
        "/api/v1/farms",
        json={
            "name": "Green Valley",
            "location": "Karnataka",
            "area": 5,
            "soil_type": "Loamy",
        },
    )

    assert farm_response.status_code == 201

    farm = farm_response.json()

    response = authenticated_client.post(
        f"/api/v1/farms/{farm['id']}/fields",
        json={
            "name": "North Field",
            "area": 2.5,
            "soil_type": "Loamy",
            "location": "North side",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "North Field"
    assert data["farm_id"] == farm["id"]
    assert data["area"] == 2.5

def test_list_fields(
    authenticated_client,
):
    farm_response = authenticated_client.post(
        "/api/v1/farms",
        json={
            "name": "Green Valley",
            "location": "Karnataka",
            "area": 5,
            "soil_type": "Loamy",
        },
    )

    farm = farm_response.json()

    authenticated_client.post(
        f"/api/v1/farms/{farm['id']}/fields",
        json={
            "name": "Field A",
            "area": 2,
        },
    )

    authenticated_client.post(
        f"/api/v1/farms/{farm['id']}/fields",
        json={
            "name": "Field B",
            "area": 3,
        },
    )

    response = authenticated_client.get(
        f"/api/v1/farms/{farm['id']}/fields"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["name"] == "Field A"
    assert data[1]["name"] == "Field B"

def test_get_field(
    authenticated_client,
):
    farm_response = authenticated_client.post(
        "/api/v1/farms",
        json={
            "name": "Green Valley",
            "location": "Karnataka",
            "area": 5,
        },
    )

    farm = farm_response.json()

    field_response = authenticated_client.post(
        f"/api/v1/farms/{farm['id']}/fields",
        json={
            "name": "North Field",
            "area": 2,
        },
    )

    field = field_response.json()

    response = authenticated_client.get(
        f"/api/v1/farms/{farm['id']}/fields/{field['id']}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == field["id"]

def test_update_field(
    authenticated_client,
):
    farm_response = authenticated_client.post(
        "/api/v1/farms",
        json={
            "name": "Green Valley",
            "location": "Karnataka",
            "area": 5,
        },
    )

    farm = farm_response.json()

    field_response = authenticated_client.post(
        f"/api/v1/farms/{farm['id']}/fields",
        json={
            "name": "Old Name",
            "area": 2,
        },
    )

    field = field_response.json()

    response = authenticated_client.put(
        f"/api/v1/farms/{farm['id']}/fields/{field['id']}",
        json={
            "name": "Updated Field",
            "area": 2.5,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Updated Field"
    assert data["area"] == 2.5

def test_delete_field(
    authenticated_client,
):
    farm_response = authenticated_client.post(
        "/api/v1/farms",
        json={
            "name": "Green Valley",
            "location": "Karnataka",
            "area": 5,
        },
    )

    farm = farm_response.json()

    field_response = authenticated_client.post(
        f"/api/v1/farms/{farm['id']}/fields",
        json={
            "name": "Field To Delete",
            "area": 2,
        },
    )

    field = field_response.json()

    delete_response = authenticated_client.delete(
        f"/api/v1/farms/{farm['id']}/fields/{field['id']}"
    )

    assert delete_response.status_code == 204

    get_response = authenticated_client.get(
        f"/api/v1/farms/{farm['id']}/fields/{field['id']}"
    )

    assert get_response.status_code == 404

def test_farmer_cannot_access_another_farm_field(
    authenticated_client,
    second_authenticated_client,
):
    farm_response = authenticated_client.post(
        "/api/v1/farms",
        json={
            "name": "Farmer A Farm",
            "location": "Karnataka",
            "area": 5,
        },
    )

    farm = farm_response.json()

    field_response = authenticated_client.post(
        f"/api/v1/farms/{farm['id']}/fields",
        json={
            "name": "Private Field",
            "area": 2,
        },
    )

    field = field_response.json()

    response = second_authenticated_client.get(
        f"/api/v1/farms/{farm['id']}/fields/{field['id']}"
    )

    assert response.status_code == 403
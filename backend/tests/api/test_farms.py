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


def test_create_crop(
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

    response = authenticated_client.post(
        f"/api/v1/farms/{farm['id']}/fields/{field['id']}/crops",
        json={
            "crop_type": "Rice",
            "variety": "Basmati",
            "planting_date": "2026-06-01",
            "expected_harvest_date": "2026-10-01",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["crop_type"] == "Rice"
    assert data["variety"] == "Basmati"
    assert data["field_id"] == field["id"]
    assert data["status"] == "planned"

def test_list_crops(
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

    for crop_name in ["Rice", "Wheat"]:
        authenticated_client.post(
            f"/api/v1/farms/{farm['id']}/fields/{field['id']}/crops",
            json={
                "crop_type": crop_name,
                "planting_date": "2026-06-01",
            },
        )

    response = authenticated_client.get(
        f"/api/v1/farms/{farm['id']}/fields/{field['id']}/crops"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["crop_type"] == "Rice"
    assert data[1]["crop_type"] == "Wheat"

def test_get_crop(
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

    crop_response = authenticated_client.post(
        f"/api/v1/farms/{farm['id']}/fields/{field['id']}/crops",
        json={
            "crop_type": "Rice",
            "planting_date": "2026-06-01",
        },
    )

    crop = crop_response.json()

    response = authenticated_client.get(
        f"/api/v1/farms/{farm['id']}/fields/{field['id']}/crops/{crop['id']}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == crop["id"]

def test_update_crop(
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

    crop_response = authenticated_client.post(
        f"/api/v1/farms/{farm['id']}/fields/{field['id']}/crops",
        json={
            "crop_type": "Rice",
            "planting_date": "2026-06-01",
        },
    )

    crop = crop_response.json()

    response = authenticated_client.put(
        f"/api/v1/farms/{farm['id']}/fields/{field['id']}/crops/{crop['id']}",
        json={
            "crop_type": "Wheat",
            "status": "active",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["crop_type"] == "Wheat"
    assert data["status"] == "active"

def test_delete_crop(
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

    crop_response = authenticated_client.post(
        f"/api/v1/farms/{farm['id']}/fields/{field['id']}/crops",
        json={
            "crop_type": "Rice",
            "planting_date": "2026-06-01",
        },
    )

    crop = crop_response.json()

    response = authenticated_client.delete(
        f"/api/v1/farms/{farm['id']}/fields/{field['id']}/crops/{crop['id']}"
    )

    assert response.status_code == 204

    get_response = authenticated_client.get(
        f"/api/v1/farms/{farm['id']}/fields/{field['id']}/crops/{crop['id']}"
    )

    assert get_response.status_code == 404

def test_farmer_cannot_access_another_farm_crop(
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

    crop_response = authenticated_client.post(
        f"/api/v1/farms/{farm['id']}/fields/{field['id']}/crops",
        json={
            "crop_type": "Rice",
            "planting_date": "2026-06-01",
        },
    )

    crop = crop_response.json()

    response = second_authenticated_client.get(
        f"/api/v1/farms/{farm['id']}/fields/{field['id']}/crops/{crop['id']}"
    )

    assert response.status_code == 403

def test_get_farm_overview(
    authenticated_client,
):
    farm_response = authenticated_client.post(
        "/api/v1/farms",
        json={
            "name": "Digital Twin Farm",
            "location": "Karnataka",
            "area": 10,
            "soil_type": "Loamy",
        },
    )

    assert farm_response.status_code == 201

    farm = farm_response.json()

    field_a_response = authenticated_client.post(
        f"/api/v1/farms/{farm['id']}/fields",
        json={
            "name": "Field A",
            "area": 4,
            "soil_type": "Loamy",
            "location": "North",
        },
    )

    assert field_a_response.status_code == 201

    field_a = field_a_response.json()

    field_b_response = authenticated_client.post(
        f"/api/v1/farms/{farm['id']}/fields",
        json={
            "name": "Field B",
            "area": 6,
            "soil_type": "Clay",
            "location": "South",
        },
    )

    assert field_b_response.status_code == 201

    field_b = field_b_response.json()

    # Two crops in Field A
    for crop_type in ["Rice", "Wheat"]:
        response = authenticated_client.post(
            f"/api/v1/farms/{farm['id']}/fields/{field_a['id']}/crops",
            json={
                "crop_type": crop_type,
                "planting_date": "2026-06-01",
            },
        )

        assert response.status_code == 201

    # One crop in Field B
    crop_response = authenticated_client.post(
        f"/api/v1/farms/{farm['id']}/fields/{field_b['id']}/crops",
        json={
            "crop_type": "Maize",
            "variety": "Hybrid",
            "planting_date": "2026-06-15",
        },
    )

    assert crop_response.status_code == 201

    response = authenticated_client.get(
        f"/api/v1/farms/{farm['id']}/overview"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == farm["id"]
    assert data["name"] == "Digital Twin Farm"
    assert data["location"] == "Karnataka"
    assert data["area"] == 10
    assert data["soil_type"] == "Loamy"

    assert data["field_count"] == 2
    assert data["crop_count"] == 3

    assert len(data["fields"]) == 2

    assert data["fields"][0]["name"] == "Field A"
    assert len(data["fields"][0]["crops"]) == 2

    assert data["fields"][1]["name"] == "Field B"
    assert len(data["fields"][1]["crops"]) == 1

    assert data["fields"][1]["crops"][0]["crop_type"] == "Maize"





def test_farmer_cannot_access_another_farm_overview(
    authenticated_client,
    second_authenticated_client,
):
    farm_response = authenticated_client.post(
        "/api/v1/farms",
        json={
            "name": "Private Farm",
            "location": "Karnataka",
            "area": 5,
        },
    )

    assert farm_response.status_code == 201

    farm = farm_response.json()

    response = second_authenticated_client.get(
        f"/api/v1/farms/{farm['id']}/overview"
    )

    assert response.status_code == 403


def test_get_missing_farm_overview(
    authenticated_client,
):
    farm_id = uuid4()

    response = authenticated_client.get(
        f"/api/v1/farms/{farm_id}/overview"
    )

    assert response.status_code == 404


def test_farm_overview_with_no_fields(
    authenticated_client,
):
    farm_response = authenticated_client.post(
        "/api/v1/farms",
        json={
            "name": "Empty Farm",
            "location": "Karnataka",
            "area": 5,
        },
    )

    assert farm_response.status_code == 201

    farm = farm_response.json()

    response = authenticated_client.get(
        f"/api/v1/farms/{farm['id']}/overview"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["field_count"] == 0
    assert data["crop_count"] == 0
    assert data["fields"] == []


def test_farm_overview_with_field_without_crops(
    authenticated_client,
):
    farm_response = authenticated_client.post(
        "/api/v1/farms",
        json={
            "name": "Field Only Farm",
            "location": "Karnataka",
            "area": 5,
        },
    )

    assert farm_response.status_code == 201

    farm = farm_response.json()

    field_response = authenticated_client.post(
        f"/api/v1/farms/{farm['id']}/fields",
        json={
            "name": "Empty Field",
            "area": 2,
            "soil_type": "Loamy",
            "location": "North",
        },
    )

    assert field_response.status_code == 201

    response = authenticated_client.get(
        f"/api/v1/farms/{farm['id']}/overview"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["field_count"] == 1
    assert data["crop_count"] == 0
    assert len(data["fields"]) == 1

    assert data["fields"][0]["name"] == "Empty Field"
    assert data["fields"][0]["crops"] == []
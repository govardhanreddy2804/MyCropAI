def test_get_notification_preferences(
    authenticated_client,
):
    response = authenticated_client.get("/api/v1/notification-preferences")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_enable_email_preference(
    authenticated_client,
):
    response = authenticated_client.put(
        "/api/v1/notification-preferences/irrigation/email",
        json={"enabled": True},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["alert_type"] == "irrigation"
    assert data["channel"] == "email"
    assert data["enabled"] is True


def test_disable_in_app_preference(
    authenticated_client,
):
    response = authenticated_client.put(
        "/api/v1/notification-preferences/irrigation/in_app",
        json={"enabled": False},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["alert_type"] == "irrigation"
    assert data["channel"] == "in_app"
    assert data["enabled"] is False


def test_update_existing_preference(
    authenticated_client,
):
    # Enable the preference first.
    response = authenticated_client.put(
        "/api/v1/notification-preferences/irrigation/email",
        json={"enabled": True},
    )

    assert response.status_code == 200
    assert response.json()["enabled"] is True

    # Disable the same preference.
    response = authenticated_client.put(
        "/api/v1/notification-preferences/irrigation/email",
        json={"enabled": False},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["alert_type"] == "irrigation"
    assert data["channel"] == "email"
    assert data["enabled"] is False


def test_get_preferences_after_update(
    authenticated_client,
):
    response = authenticated_client.put(
        "/api/v1/notification-preferences/irrigation/email",
        json={"enabled": True},
    )

    assert response.status_code == 200

    response = authenticated_client.get("/api/v1/notification-preferences")

    assert response.status_code == 200

    preferences = response.json()

    irrigation_email = next(
        (
            preference
            for preference in preferences
            if preference["alert_type"] == "irrigation"
            and preference["channel"] == "email"
        ),
        None,
    )

    assert irrigation_email is not None
    assert irrigation_email["enabled"] is True


def test_invalid_alert_type(
    authenticated_client,
):
    response = authenticated_client.put(
        "/api/v1/notification-preferences/invalid/email",
        json={"enabled": True},
    )

    assert response.status_code == 422


def test_invalid_channel(
    authenticated_client,
):
    response = authenticated_client.put(
        "/api/v1/notification-preferences/irrigation/invalid",
        json={"enabled": True},
    )

    assert response.status_code == 422

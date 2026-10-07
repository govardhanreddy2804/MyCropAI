from app.models.enums import AlertType, NotificationChannel
from app.services.notification_preference import (
    get_user_preferences,
    is_channel_enabled,
    set_user_preference,
)


def test_in_app_is_enabled_by_default(db_session, test_user):
    enabled = is_channel_enabled(
        db=db_session,
        user_id=test_user.id,
        alert_type=AlertType.IRRIGATION,
        channel=NotificationChannel.IN_APP,
    )

    assert enabled is True


def test_email_is_disabled_by_default(db_session, test_user):
    enabled = is_channel_enabled(
        db=db_session,
        user_id=test_user.id,
        alert_type=AlertType.IRRIGATION,
        channel=NotificationChannel.EMAIL,
    )

    assert enabled is False


def test_can_enable_email(db_session, test_user):
    preference = set_user_preference(
        db=db_session,
        user_id=test_user.id,
        alert_type=AlertType.IRRIGATION,
        channel=NotificationChannel.EMAIL,
        enabled=True,
    )

    assert preference.enabled is True

    enabled = is_channel_enabled(
        db=db_session,
        user_id=test_user.id,
        alert_type=AlertType.IRRIGATION,
        channel=NotificationChannel.EMAIL,
    )

    assert enabled is True


def test_can_disable_in_app(db_session, test_user):
    preference = set_user_preference(
        db=db_session,
        user_id=test_user.id,
        alert_type=AlertType.IRRIGATION,
        channel=NotificationChannel.IN_APP,
        enabled=False,
    )

    assert preference.enabled is False

    enabled = is_channel_enabled(
        db=db_session,
        user_id=test_user.id,
        alert_type=AlertType.IRRIGATION,
        channel=NotificationChannel.IN_APP,
    )

    assert enabled is False


def test_updating_existing_preference_does_not_create_duplicate(
    db_session,
    test_user,
):
    first = set_user_preference(
        db=db_session,
        user_id=test_user.id,
        alert_type=AlertType.IRRIGATION,
        channel=NotificationChannel.EMAIL,
        enabled=True,
    )

    second = set_user_preference(
        db=db_session,
        user_id=test_user.id,
        alert_type=AlertType.IRRIGATION,
        channel=NotificationChannel.EMAIL,
        enabled=False,
    )

    assert first.id == second.id
    assert second.enabled is False

    preferences = get_user_preferences(
        db=db_session,
        user_id=test_user.id,
    )

    matching = [
        preference
        for preference in preferences
        if preference.alert_type == AlertType.IRRIGATION
        and preference.channel == NotificationChannel.EMAIL
    ]

    assert len(matching) == 1

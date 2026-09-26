from app.services.irrigation.crop_profile import (
    DEFAULT_CROP_PROFILE,
    get_crop_water_profile,
)


def test_known_crop_profile():
    profile = get_crop_water_profile("maize")

    assert profile.crop_type == "maize"
    assert profile.moisture_threshold > 0


def test_crop_lookup_is_case_insensitive():
    profile = get_crop_water_profile("MAIZE")

    assert profile.crop_type == "maize"


def test_unknown_crop_uses_default_profile():
    profile = get_crop_water_profile(
        "some-unknown-crop"
    )

    assert profile == DEFAULT_CROP_PROFILE
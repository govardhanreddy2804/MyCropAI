from dataclasses import dataclass


@dataclass(frozen=True)
class CropWaterProfile:
    crop_type: str
    moisture_threshold: float
    base_confidence: float = 0.50


DEFAULT_CROP_PROFILE = CropWaterProfile(
    crop_type="default",
    moisture_threshold=40.0,
)


CROP_PROFILES: dict[str, CropWaterProfile] = {
    "rice": CropWaterProfile(
        crop_type="rice",
        moisture_threshold=50.0,
        base_confidence=0.60,
    ),
    "maize": CropWaterProfile(
        crop_type="maize",
        moisture_threshold=40.0,
        base_confidence=0.55,
    ),
    "cotton": CropWaterProfile(
        crop_type="cotton",
        moisture_threshold=38.0,
        base_confidence=0.55,
    ),
    "groundnut": CropWaterProfile(
        crop_type="groundnut",
        moisture_threshold=40.0,
        base_confidence=0.55,
    ),
    "tomato": CropWaterProfile(
        crop_type="tomato",
        moisture_threshold=45.0,
        base_confidence=0.60,
    ),
}


def get_crop_water_profile(
    crop_type: str,
) -> CropWaterProfile:

    return CROP_PROFILES.get(
        crop_type.strip().lower(),
        DEFAULT_CROP_PROFILE,
    )
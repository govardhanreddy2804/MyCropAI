from app.models.enums import ObservationSource, ObservationType


SOURCE_PRIORITY: dict[
    ObservationType,
    dict[ObservationSource, int],
] = {
    ObservationType.SOIL_MOISTURE: {
        ObservationSource.IOT_SENSOR: 100,
        ObservationSource.MANUAL: 90,
        ObservationSource.SATELLITE: 60,
        ObservationSource.SOIL_API: 40,
    },

    ObservationType.SOIL_PH: {
        ObservationSource.MANUAL: 100,
        ObservationSource.SOIL_API: 70,
        ObservationSource.SATELLITE: 40,
        ObservationSource.IOT_SENSOR: 30,
    },

    ObservationType.SOIL_TEMPERATURE: {
        ObservationSource.IOT_SENSOR: 100,
        ObservationSource.MANUAL: 90,
        ObservationSource.SOIL_API: 50,
        ObservationSource.SATELLITE: 40,
    },

    ObservationType.NITROGEN: {
        ObservationSource.MANUAL: 100,
        ObservationSource.SOIL_API: 80,
        ObservationSource.SATELLITE: 50,
        ObservationSource.IOT_SENSOR: 40,
    },

    ObservationType.PHOSPHORUS: {
        ObservationSource.MANUAL: 100,
        ObservationSource.SOIL_API: 80,
        ObservationSource.SATELLITE: 50,
        ObservationSource.IOT_SENSOR: 40,
    },

    ObservationType.POTASSIUM: {
        ObservationSource.MANUAL: 100,
        ObservationSource.SOIL_API: 80,
        ObservationSource.SATELLITE: 50,
        ObservationSource.IOT_SENSOR: 40,
    },

    ObservationType.AIR_TEMPERATURE: {
        ObservationSource.IOT_SENSOR: 100,
        ObservationSource.WEATHER_API: 90,
        ObservationSource.MANUAL: 70,
        ObservationSource.SATELLITE: 50,
    },

    ObservationType.AIR_HUMIDITY: {
        ObservationSource.IOT_SENSOR: 100,
        ObservationSource.WEATHER_API: 90,
        ObservationSource.MANUAL: 70,
        ObservationSource.SATELLITE: 50,
    },

    ObservationType.RAINFALL: {
        ObservationSource.IOT_SENSOR: 100,
        ObservationSource.WEATHER_API: 90,
        ObservationSource.MANUAL: 80,
        ObservationSource.SATELLITE: 60,
    },

    ObservationType.WIND_SPEED: {
        ObservationSource.IOT_SENSOR: 100,
        ObservationSource.WEATHER_API: 90,
        ObservationSource.MANUAL: 70,
        ObservationSource.SATELLITE: 50,
    },

    ObservationType.LIGHT_INTENSITY: {
        ObservationSource.IOT_SENSOR: 100,
        ObservationSource.MANUAL: 80,
        ObservationSource.SATELLITE: 70,
    },
}


def get_source_priority(
    observation_type: ObservationType,
    source: ObservationSource,
) -> int:
    return SOURCE_PRIORITY.get(
        observation_type,
        {},
    ).get(source, 0)
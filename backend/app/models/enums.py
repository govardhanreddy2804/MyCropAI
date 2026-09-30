from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    FARMER = "farmer"
    AGRONOMIST = "agronomist"


class CropStatus(str, Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    HARVESTED = "harvested"
    FAILED = "failed"


class ObservationSource(str, Enum):
    MANUAL = "manual"
    WEATHER_API = "weather_api"
    SOIL_API = "soil_api"
    SATELLITE = "satellite"
    IOT_SENSOR = "iot_sensor"


class ObservationType(str, Enum):
    SOIL_MOISTURE = "soil_moisture"
    SOIL_TEMPERATURE = "soil_temperature"
    SOIL_PH = "soil_ph"

    NITROGEN = "nitrogen"
    PHOSPHORUS = "phosphorus"
    POTASSIUM = "potassium"

    AIR_TEMPERATURE = "air_temperature"
    AIR_HUMIDITY = "air_humidity"

    RAINFALL = "rainfall"
    WIND_SPEED = "wind_speed"
    LIGHT_INTENSITY = "light_intensity"


class AlertType(str, Enum):
    IRRIGATION = "irrigation"
    WEATHER = "weather"
    DISEASE = "disease"
    CROP_HEALTH = "crop_health"
    SYSTEM = "system"


class AlertStatus(str, Enum):
    UNREAD = "unread"
    READ = "read"
    ACKNOWLEDGED = "acknowledged"
    EXPIRED = "expired"


class AlertPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
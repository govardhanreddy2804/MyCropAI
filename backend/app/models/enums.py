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
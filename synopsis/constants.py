from .ext_models import DeclEnum


class HostCheckState(DeclEnum):
    up = "UP", "Host Up"
    down = "DOWN", "Host Down"
    error = "ERROR", "Error retrieving state"
    unknown = "UNKNOWN", "Cannot determine state"
    pending = "PENDING", "Data not yet available"


class ServiceCheckState(DeclEnum):
    good = "GOOD", "Healthy"
    warning = "WARNING", "Unhealthy"
    critical = "CRITICAL", "Bad state"
    error = "ERROR", "Error retrieving state"
    unknown = "UNKNOWN", "Cannot determine state"
    pending = "PENDING", "Data not yet available"


class HostServiceState(DeclEnum):
    active = "ACTIVE", "Active"
    inactive = "INACTIVE", "Inactive"
    maintenance = "MAINT", "Maintenance"
    decommissioned = "DECOM", "Decommissioned"

from enum import Enum

class IncidentStatus(Enum):
    new = "new"
    completed = "completed"
    failed = "failed"


class IncidentSource(Enum):
    operator = "operator"
    monitoring = "monitoring"
    partner = "partner"
from pydantic import BaseModel, field_validator, Field, field_serializer
from datetime import datetime
from enums.inedent import IncidentStatus, IncidentSource


class Incident(BaseModel):
    incident_message: str = Field(min_length=5, max_length=1000, description="Текст происшествия")
    incident_type: IncidentStatus
    source: IncidentSource

    @field_validator("incident_message")
    def validate_message(cls, value: str):
        forbidden = {"test", "none", "null"}
        if value.lower() in forbidden:
            raise ValueError("Invalid incident message")
        return value.strip()

class IncidentResponse(BaseModel):
    incident_id: int = Field(..., description="Уникальный идентификатор инцидента")
    incident_message: str = Field(..., description="Сообщение об ошибке или проблеме")
    incident_type: IncidentStatus = Field(..., description="Тип инцидента (info, warning, critical)")
    source: IncidentSource = Field(..., description="Источник инцидента")
    created_at: datetime = Field(..., description="Дата и время создания инцидента")

    model_config = {
        "from_attributes": True  # 👈 включаем поддержку from_orm
    }

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")

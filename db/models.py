from datetime import datetime
import uuid

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, DateTime, JSON, MetaData, Boolean, Integer, Enum

from .utils import conventions
from enums.inedent import IncidentStatus, IncidentSource


meta = MetaData(naming_convention=conventions)
Base = declarative_base(metadata=meta)


class Incident(Base):
    __tablename__ = "Incident"
    incident_id = Column(Integer, primary_key=True, autoincrement=True)
    incident_message = Column(String)
    incident_type = Column(Enum(IncidentStatus))
    source = Column(Enum(IncidentSource))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)



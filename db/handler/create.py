from schemas.incident import Incident
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Incident as IncidentModel

async def create_incident(incident: Incident, db: AsyncSession):
    incident = IncidentModel(**incident.model_dump())
    db.add(incident)
    await db.commit()
    await db.refresh(incident)
    return incident

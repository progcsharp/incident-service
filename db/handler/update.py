from enums.inedent import IncidentStatus
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Incident
from sqlalchemy import select
from fastapi import HTTPException

async def update_incident_status(incident_id: int, status: IncidentStatus, db: AsyncSession):
    result = await db.execute(select(Incident).where(Incident.incident_id == incident_id))
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Обновляем статус прямо в объекте
    incident.incident_type = status

    # Фиксируем изменения
    await db.commit()
    await db.refresh(incident)

    return incident

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from db.models import Incident
from enums.inedent import IncidentStatus, IncidentSource

async def get_incident(incident_id: int, db: AsyncSession):
    incident = await db.execute(select(Incident).where(Incident.incident_id == incident_id))
    return incident.scalar_one_or_none()

async def get_incident_list(page: int, limit: int, status: IncidentStatus, source: IncidentSource, db: AsyncSession):
    query = select(Incident)

    # Добавляем фильтры, только если они переданы
    filters = []
    if status is not None:
        filters.append(Incident.incident_type == status)
    if source is not None:
        filters.append(Incident.source == source)

    if filters:
        query = query.where(and_(*filters))  # объединяем через AND

    # Пагинация и сортировка
    query = query.offset((page - 1) * limit).limit(limit).order_by(Incident.created_at.desc())

    # Выполняем запрос
    result = await db.execute(query)
    return result.scalars().all()

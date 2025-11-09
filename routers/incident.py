from fastapi import APIRouter, Depends, HTTPException
from schemas.incident import Incident, IncidentResponse
from db.handler.get import get_incident, get_incident_list as get_incident_list_handler
from db.handler.create import create_incident as create_incident_handler
from db.handler.update import update_incident_status as update_incident_status_handler
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from db.engine import get_db
from enums.inedent import IncidentStatus, IncidentSource
from redis.asyncio import Redis
from redis_core.redis import get_redis
import json
from utils.logging import log_route


router = APIRouter(prefix="/incident", tags=["incident"])

@router.post("/create")
@log_route()
async def create_incident(incident: Incident, db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)):
    async with db() as session:
        try:
            incident = await create_incident_handler(incident, session)
            keys = await redis.keys("incidents:*")
            if keys:
                await redis.delete(*keys)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to create incident")
    return {"message": "Incident created"}

@router.get("/get", response_model=List[IncidentResponse])
@log_route()
async def get_incident_list(page: int = 1, limit: int = 10, status: IncidentStatus = None, source: IncidentSource = None, db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)):
    cache_key = f"incidents:{page}:{limit}:{status or 'any'}:{source or 'any'}"
    cached_data = await redis.get(cache_key)
    if cached_data:
        return json.loads(cached_data)
    async with db() as session:
        print(page, limit, status, source)
        try:
            incidents = await get_incident_list_handler(page, limit, status, source, session)
            serialized_incidents = [
                IncidentResponse.from_orm(inc).model_dump(mode="json") 
                for inc in incidents
            ]
            await redis.set(cache_key, json.dumps(serialized_incidents), ex=3600)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to get incident list")
        return incidents

@router.get("/get/{incident_id}", response_model=IncidentResponse)
@log_route()
async def get_incident_by_id(incident_id: int, db: AsyncSession = Depends(get_db)):
    async with db() as session:
        try:
            incident = await get_incident(incident_id, session)
            if not incident:
                raise HTTPException(status_code=404, detail="Incident not found")
        
        except HTTPException:
            raise 

        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to get incident")
        return incident

@router.patch("/update-status", response_model=IncidentResponse)
@log_route()
async def update_incident_status(incident_id: int, status: IncidentStatus, db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)):
    async with db() as session:
        try:
            incident = await update_incident_status_handler(incident_id, status, session)
            keys = await redis.keys("incidents:*")
            if keys:
                await redis.delete(*keys)
        except HTTPException:
            raise 
        
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to update incident status")
    return incident

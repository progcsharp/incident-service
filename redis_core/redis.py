from redis.asyncio import Redis
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from config import REDIS_HOST, REDIS_PORT, REDIS_DB

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB) 
    try:
        await redis.ping()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to Redis: {e}")
    
    app.state.redis = redis
    
    yield

    if redis:
        await redis.close()


async def get_redis(request: Request):
    # try:
    yield request.app.state.redis
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Failed to get Redis")
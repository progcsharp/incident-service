from fastapi import FastAPI, Request
from redis_core.redis import lifespan
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from routers.incident import router as incident_router

app = FastAPI(debug=False, lifespan=lifespan)


app.include_router(incident_router)

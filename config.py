from dotenv import load_dotenv
import os
from redis.asyncio import Redis
from contextlib import asynccontextmanager
from fastapi import FastAPI

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_DB = os.getenv("REDIS_DB")

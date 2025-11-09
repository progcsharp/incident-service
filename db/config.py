"""
Конфигурация базы данных
"""
import os
from functools import lru_cache

from dotenv import load_dotenv

class DatabaseConfig:
    """Конфигурация для подключения к базе данных"""
    
    def __init__(self):

        load_dotenv()
        # Получаем URL базы данных из переменной окружения или используем значение по умолчанию
        db_name = os.getenv("POSTGRES_DB", "fastapi_test")
        db_user = os.getenv("POSTGRES_USER", "postgres")
        db_password = os.getenv("POSTGRES_PASSWORD", "147896325")
        db_host = os.getenv("POSTGRES_HOST", "localhost")
        db_port = os.getenv("POSTGRES_PORT", "5432")
        self.database_url = (
            f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        )

        print(self.database_url)
        
        # Настройки пула соединений
        self.pool_size = int(os.getenv("DB_POOL_SIZE", "20"))
        self.max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "0"))
        self.echo = os.getenv("DB_ECHO", "True").lower() == "true"
        
    @property
    def sync_database_url(self) -> str:
        """Синхронный URL для создания таблиц и миграций"""
        return self.database_url.replace("+asyncpg", "").replace("+asyncio", "")


@lru_cache()
def get_database_config() -> DatabaseConfig:
    """Получить конфигурацию базы данных (с кешированием)"""
    return DatabaseConfig()

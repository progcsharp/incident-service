from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from .config import get_database_config

# Получаем конфигурацию базы данных
db_config = get_database_config()

# Создаем асинхронный движок
engine = create_async_engine(
    db_config.database_url,
    echo=db_config.echo,
    pool_size=db_config.pool_size,
    max_overflow=db_config.max_overflow
)

# Создаем фабрику сессий
SessionLocal = async_sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine, 
    expire_on_commit=False,
    class_=AsyncSession,
)



class DBContext:

    def __init__(self):
        self.db = SessionLocal()

    def __enter__(self):
        return self.db

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.close()


async def get_db():
    # try:
    yield SessionLocal
# except SQLAlchemyError as e:
#     print(e)

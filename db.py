from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from config import settings


SQLALCHEMY_DB_URL = settings.SQLALCHEMY_DB_URL


engine = create_async_engine(
	SQLALCHEMY_DB_URL,
	echo=True
)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
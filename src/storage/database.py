from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import config
from src.storage.models import Base


engine = create_async_engine(config.get('DATABASE_URL'), echo=True)

session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


from typing import AsyncGenerator
import structlog
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from app.core.config import settings

logger = structlog.get_logger()

# Create SQLAlchemy Base for all PostgreSQL models
Base = declarative_base()

# Init engine
engine = create_async_engine(
    settings.POSTGRES_URI,
    echo=False,
    future=True,
    pool_size=5,
    max_overflow=10,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_pg_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a PostgreSQL session.
    Automatically handles commit/rollback and closes the session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error("PostgreSQL Session Rollback", error=str(e))
            await session.rollback()
            raise
        finally:
            await session.close()

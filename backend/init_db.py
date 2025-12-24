import asyncio
import logging
from app.db.session import engine
from app.models.base_class import Base
# Importar modelos para que Base los detecte
from app.models.user import User
from app.models.task import Task
from app.models.message import Message
from app.models.artifact import Artifact

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db():
    async with engine.begin() as conn:
        logger.info("Creando tablas en la base de datos...")
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Tablas creadas exitosamente!")

if __name__ == "__main__":
    asyncio.run(init_db())

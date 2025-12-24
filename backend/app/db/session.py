from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import os

print(f"--- DB SESSION INIT ---")
print(f"Calculated DB URI: {settings.sqlalchemy_database_uri}")

# Log to a file we can read later
try:
    with open("D:/OSIRIS/backend/db_path_debug.txt", "w") as f:
        f.write(f"CWD: {os.getcwd()}\n")
        f.write(f"URI: {settings.sqlalchemy_database_uri}\n")
except Exception as e:
    print(f"Could not write debug file: {e}")

engine = create_async_engine(
    settings.sqlalchemy_database_uri,
    echo=True, # Log SQL for debug
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

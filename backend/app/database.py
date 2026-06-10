from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client = AsyncIOMotorClient(settings.MONGODB_URL)
db = client[settings.DATABASE_NAME]

users_collection = db.users


async def init_db():
    await users_collection.create_index("username", unique=True)

from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGODB_URI, DATABASE_NAME
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from bson.objectid import ObjectId
from typing import Optional, Dict
from pymongo import ReturnDocument

class Database:
    def __init__(self, uri: str, db_name: str):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db_name]

    async def add_user(self, fullname: str, email: str, password: str, user_type: str) -> Optional[Dict]:
        existing = await self.db.users.find_one({"email": email})
        if existing:
            return None
        password_hash = generate_password_hash(password)
        doc = {
            "fullname": fullname,
            "email": email,
            "user_type": user_type,
            "password_hash": password_hash,
            "created_at": datetime.now(timezone.utc)
        }
        res = await self.db.users.insert_one(doc)
        user = await self.db.users.find_one({"_id": res.inserted_id}, {"password_hash": 0})
        if user:
            user["id"] = str(user.pop("_id"))
        return user

    async def login_user(self, email: str, password: str) -> Optional[Dict]:
        user = await self.db.users.find_one({"email": email})
        print(user)
        if not user:
            return None
        if not check_password_hash(user.get("password_hash", ""), password):
            return None
        user.pop("password_hash", None)
        user["id"] = str(user.pop("_id"))
        return user
    
    async def change_user_type(self, email: str, new_type: str) -> Optional[Dict]:
        user = await self.db.users.find_one_and_update(
            {"email": email},
            {"$set": {"user_type": new_type}},
            return_document=ReturnDocument.AFTER
        )
        if not user:
            return None
        user.pop("password_hash", None)
        user["id"] = str(user.pop("_id"))
        return user
    

_db_instance: Optional[Database] = None

def get_database() -> Database:
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(MONGODB_URI, DATABASE_NAME)
    return _db_instance

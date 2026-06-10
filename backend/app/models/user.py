from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return str(v)


class PasskeyCredential(BaseModel):
    credential_id: str
    public_key: str
    counter: int = 0
    device_name: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)


class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    username: str
    password_hash: str
    totp_secret: Optional[str] = None
    totp_enabled: bool = False
    passkeys: List[PasskeyCredential] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    totp_enabled: bool
    has_passkeys: bool

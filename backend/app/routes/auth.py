from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bson import ObjectId
from app.models.user import UserCreate, User, UserResponse
from app.database import users_collection
from app.services.auth_service import (
    hash_password, verify_password, create_jwt_token, decode_jwt_token
)

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_jwt_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Nieprawidłowy token")

    user = await users_collection.find_one({"_id": ObjectId(payload["user_id"])})
    if not user:
        raise HTTPException(status_code=401, detail="Użytkownik nie znaleziony")

    return user


@router.post("/register")
async def register(user_data: UserCreate):
    existing = await users_collection.find_one({"username": user_data.username})
    if existing:
        raise HTTPException(status_code=400, detail="Nazwa użytkownika jest już zajęta")

    user = {
        "username": user_data.username,
        "password_hash": hash_password(user_data.password),
        "totp_secret": None,
        "totp_enabled": False,
        "passkeys": [],
        "created_at": __import__("datetime").datetime.utcnow()
    }

    result = await users_collection.insert_one(user)

    token = create_jwt_token({
        "user_id": str(result.inserted_id),
        "username": user_data.username
    })

    return {
        "message": "Konto zostało utworzone",
        "user_id": str(result.inserted_id),
        "token": token
    }


@router.post("/login")
async def login(user_data: UserCreate):
    user = await users_collection.find_one({"username": user_data.username})
    if not user:
        raise HTTPException(status_code=401, detail="Nieprawidłowa nazwa użytkownika lub hasło")

    if not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Nieprawidłowa nazwa użytkownika lub hasło")

    has_2fa = user.get("totp_enabled", False) or len(user.get("passkeys", [])) > 0

    if has_2fa:
        token = create_jwt_token({
            "user_id": str(user["_id"]),
            "username": user["username"],
            "pending_2fa": True
        }, expires_delta=__import__("datetime").timedelta(minutes=10))

        return {
            "requires_2fa": True,
            "temp_token": token,
            "totp_enabled": user.get("totp_enabled", False),
            "has_passkeys": len(user.get("passkeys", [])) > 0
        }
    else:
        token = create_jwt_token({
            "user_id": str(user["_id"]),
            "username": user["username"]
        })

        return {
            "requires_2fa": False,
            "token": token,
            "user": UserResponse(
                id=str(user["_id"]),
                username=user["username"],
                totp_enabled=False,
                has_passkeys=False
            )
        }


@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    return UserResponse(
        id=str(user["_id"]),
        username=user["username"],
        totp_enabled=user.get("totp_enabled", False),
        has_passkeys=len(user.get("passkeys", [])) > 0
    )

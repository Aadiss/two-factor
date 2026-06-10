from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from bson import ObjectId
from app.database import users_collection
from app.services.auth_service import decode_jwt_token, create_jwt_token
from app.services.totp_service import (
    generate_totp_secret, get_totp_uri, verify_totp, generate_qr_code_base64
)
from app.services.passkey_service import (
    generate_registration_options, complete_registration,
    generate_authentication_options, complete_authentication
)

router = APIRouter(prefix="/api/2fa", tags=["2fa"])
security = HTTPBearer()


async def get_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = decode_jwt_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Nieprawidłowy token")

    user = await users_collection.find_one({"_id": ObjectId(payload["user_id"])})
    if not user:
        raise HTTPException(status_code=401, detail="Użytkownik nie znaleziony")

    return user, payload


class VerifyTOTP(BaseModel):
    code: str


class PasskeyRegisterComplete(BaseModel):
    id: str
    rawId: str
    response: dict
    state: str


class PasskeyAuthComplete(BaseModel):
    id: str
    rawId: str
    response: dict
    state: str


@router.post("/totp/setup")
async def setup_totp(user: dict = Depends(get_user_from_token)):
    user_data = user[0]

    if user_data.get("totp_enabled"):
        raise HTTPException(status_code=400, detail="TOTP jest już włączony")

    secret = generate_totp_secret()
    uri = get_totp_uri(secret, user_data["username"])
    qr_code = generate_qr_code_base64(uri)

    await users_collection.update_one(
        {"_id": user_data["_id"]},
        {"$set": {"totp_secret": secret}}
    )

    return {
        "secret": secret,
        "qr_code": qr_code,
        "uri": uri
    }


@router.post("/totp/verify")
async def verify_totp_setup(data: VerifyTOTP, user: dict = Depends(get_user_from_token)):
    user_data = user[0]

    if not user_data.get("totp_secret"):
        raise HTTPException(status_code=400, detail="Konfiguracja TOTP nie została rozpoczęta")

    if not verify_totp(user_data["totp_secret"], data.code):
        raise HTTPException(status_code=400, detail="Nieprawidłowy kod TOTP")

    await users_collection.update_one(
        {"_id": user_data["_id"]},
        {"$set": {"totp_enabled": True}}
    )

    return {"message": "TOTP został pomyślnie włączony"}


@router.post("/totp/validate")
async def validate_totp(data: VerifyTOTP, user: dict = Depends(get_user_from_token)):
    user_data, payload = user

    if not user_data.get("totp_enabled") or not user_data.get("totp_secret"):
        raise HTTPException(status_code=400, detail="TOTP nie jest włączony")

    if not verify_totp(user_data["totp_secret"], data.code):
        raise HTTPException(status_code=400, detail="Nieprawidłowy kod TOTP")

    if payload.get("pending_2fa"):
        token = create_jwt_token({
            "user_id": str(user_data["_id"]),
            "username": user_data["username"]
        })
        return {"token": token, "verified": True}

    return {"verified": True}


@router.delete("/totp")
async def disable_totp(user: dict = Depends(get_user_from_token)):
    user_data = user[0]

    await users_collection.update_one(
        {"_id": user_data["_id"]},
        {"$set": {"totp_enabled": False, "totp_secret": None}}
    )

    return {"message": "TOTP został pomyślnie wyłączony"}


@router.post("/passkey/register/begin")
async def passkey_register_begin(user: dict = Depends(get_user_from_token)):
    user_data = user[0]

    result = generate_registration_options(
        user_data["username"],
        str(user_data["_id"])
    )

    return {
        "options": result["options"],
        "state": result["_state"]
    }


@router.post("/passkey/register/complete")
async def passkey_register_complete(data: PasskeyRegisterComplete, user: dict = Depends(get_user_from_token)):
    user_data = user[0]

    result = complete_registration(data.state, {
        "id": data.id,
        "response": data.response
    })

    passkey = {
        "credential_id": result["credential_id"],
        "public_key": result["public_key"],
        "credential_data": result["credential_data"],
        "counter": result["sign_count"],
        "device_name": f"Klucz bezpieczeństwa {len(user_data.get('passkeys', [])) + 1}",
        "created_at": __import__("datetime").datetime.utcnow()
    }

    await users_collection.update_one(
        {"_id": user_data["_id"]},
        {"$push": {"passkeys": passkey}}
    )

    return {"message": "Klucz bezpieczeństwa został pomyślnie zarejestrowany"}


@router.post("/passkey/authenticate/begin")
async def passkey_authenticate_begin(user: dict = Depends(get_user_from_token)):
    user_data = user[0]
    passkeys = user_data.get("passkeys", [])

    if not passkeys:
        raise HTTPException(status_code=400, detail="Brak zarejestrowanych kluczy bezpieczeństwa")

    credentials = [
        {"credential_id": pk["credential_id"], "credential_data": pk.get("credential_data", "")}
        for pk in passkeys
    ]

    result = generate_authentication_options(credentials)

    return {
        "options": result["options"],
        "state": result["_state"]
    }


@router.post("/passkey/authenticate/complete")
async def passkey_authenticate_complete(data: PasskeyAuthComplete, user: dict = Depends(get_user_from_token)):
    user_data, payload = user
    passkeys = user_data.get("passkeys", [])

    credential = None
    for pk in passkeys:
        stored_id = pk["credential_id"]
        browser_id = data.id
        if stored_id == browser_id or stored_id.replace("+", "-").replace("/", "_").rstrip("=") == browser_id:
            credential = pk
            break

    if not credential:
        raise HTTPException(status_code=400, detail="Klucz bezpieczeństwa nie znaleziony")

    result = complete_authentication(
        data.state,
        {"id": data.id, "rawId": data.rawId, "response": data.response},
        credential.get("credential_data", ""),
        credential["counter"]
    )

    await users_collection.update_one(
        {"_id": user_data["_id"], "passkeys.credential_id": data.id},
        {"$set": {"passkeys.$.counter": result["new_count"]}}
    )

    if payload.get("pending_2fa"):
        token = create_jwt_token({
            "user_id": str(user_data["_id"]),
            "username": user_data["username"]
        })
        return {"token": token, "verified": True}

    return {"verified": True}


@router.get("/passkey/list")
async def list_passkeys(user: dict = Depends(get_user_from_token)):
    user_data = user[0]
    passkeys = user_data.get("passkeys", [])

    return [
        {
            "credential_id": pk["credential_id"],
            "device_name": pk.get("device_name", ""),
            "created_at": pk["created_at"]
        }
        for pk in passkeys
    ]


@router.delete("/passkey/{credential_id}")
async def delete_passkey(credential_id: str, user: dict = Depends(get_user_from_token)):
    user_data = user[0]

    result = await users_collection.update_one(
        {"_id": user_data["_id"]},
        {"$pull": {"passkeys": {"credential_id": credential_id}}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Klucz bezpieczeństwa nie znaleziony")

    return {"message": "Klucz bezpieczeństwa został pomyślnie usunięty"}

import json
import base64
from fido2.features import webauthn_json_mapping
webauthn_json_mapping.enabled = True
from fido2.server import Fido2Server
from fido2.webauthn import PublicKeyCredentialRpEntity, PublicKeyCredentialUserEntity, AttestedCredentialData
from fido2 import cbor
from app.config import settings


def _verify_origin(origin: str) -> bool:
    return origin == settings.RP_ORIGIN

rp = PublicKeyCredentialRpEntity(id=settings.RP_ID, name=settings.RP_NAME)
server = Fido2Server(rp, verify_origin=_verify_origin)


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(data: str) -> bytes:
    padding = 4 - len(data) % 4
    data += "=" * padding
    return base64.urlsafe_b64decode(data)


def _options_to_dict(options) -> dict:
    pk = options.public_key
    result = {
        "rp": {"name": pk.rp.name, "id": pk.rp.id},
        "user": {
            "id": _b64url_encode(pk.user.id),
            "name": pk.user.name,
            "displayName": pk.user.display_name,
        },
        "challenge": _b64url_encode(pk.challenge),
        "pubKeyCredParams": [
            {"type": p.type, "alg": p.alg} for p in pk.pub_key_cred_params
        ],
        "timeout": pk.timeout,
        "attestation": pk.attestation,
    }

    if pk.exclude_credentials:
        result["excludeCredentials"] = [
            {"type": c.type, "id": _b64url_encode(c.id)}
            for c in pk.exclude_credentials
        ]

    if pk.authenticator_selection:
        auth_sel = pk.authenticator_selection
        sel = {}
        if auth_sel.authenticator_attachment:
            sel["authenticatorAttachment"] = auth_sel.authenticator_attachment
        if auth_sel.resident_key:
            sel["residentKey"] = auth_sel.resident_key
        if auth_sel.require_resident_key is not None:
            sel["requireResidentKey"] = auth_sel.require_resident_key
        if auth_sel.user_verification:
            sel["userVerification"] = auth_sel.user_verification
        result["authenticatorSelection"] = sel

    return result


def _auth_options_to_dict(options) -> dict:
    pk = options.public_key
    result = {
        "challenge": _b64url_encode(pk.challenge),
        "timeout": pk.timeout,
        "rpId": pk.rp_id,
    }

    if pk.allow_credentials:
        result["allowCredentials"] = [
            {"type": c.type, "id": _b64url_encode(c.id), "transports": getattr(c, "transports", None) or []}
            for c in pk.allow_credentials
        ]

    if pk.user_verification:
        result["userVerification"] = pk.user_verification

    return result


def generate_registration_options(username: str, user_id: str) -> dict:
    user = PublicKeyCredentialUserEntity(
        id=user_id.encode(),
        name=username,
        display_name=username
    )

    options, state = server.register_begin(
        user,
        [],
        user_verification="discouraged"
    )

    return {
        "options": _options_to_dict(options),
        "_state": base64.b64encode(json.dumps(state).encode()).decode()
    }


def complete_registration(state_b64: str, credential_data: dict) -> dict:
    state = json.loads(base64.b64decode(state_b64))
    auth_data = server.register_complete(state, credential_data)
    return {
        "credential_id": _b64url_encode(auth_data.credential_data.credential_id),
        "public_key": base64.b64encode(cbor.encode(auth_data.credential_data.public_key)).decode(),
        "credential_data": base64.b64encode(bytes(auth_data.credential_data)).decode(),
        "sign_count": auth_data.counter
    }


def generate_authentication_options(credentials: list) -> dict:
    attested_creds = []
    for cred in credentials:
        blob = cred.get("credential_data", "")
        if blob:
            attested_creds.append(AttestedCredentialData(base64.b64decode(blob)))

    options, state = server.authenticate_begin(
        credentials=attested_creds or None,
        user_verification="discouraged"
    )

    return {
        "options": _auth_options_to_dict(options),
        "_state": base64.b64encode(json.dumps(state).encode()).decode()
    }


def complete_authentication(state_b64: str, full_response: dict, credential_data_blob: str, current_count: int) -> dict:
    state = json.loads(base64.b64decode(state_b64))

    cred = AttestedCredentialData(base64.b64decode(credential_data_blob))
    server.authenticate_complete(state, [cred], full_response)

    return {"verified": True, "new_count": current_count + 1}

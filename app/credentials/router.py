from fastapi import APIRouter, HTTPException, Request

from app.shared.dependencies.db import PostgresRunnerDep
from app.auth.dependencies import CurrentSubjectDep
from app.auth.enums import AccessLevel
from app.auth.decorators import authorize
from app.audit.decorators import audit

from .dto import PublicKeyResponse
from . import service as credentials_service

router = APIRouter()


@router.get("/public-key")
@audit()
@authorize(AccessLevel.UNCLASSIFIED)
async def read_public_key(
    db: PostgresRunnerDep, subject: CurrentSubjectDep, request: Request
) -> PublicKeyResponse:
    """Return the server's public key for encrypting data."""
    try:
        return credentials_service.get_public_key(db=db)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to load public key")

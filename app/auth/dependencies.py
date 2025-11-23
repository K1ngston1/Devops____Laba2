from fastapi import Header, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated

from app.auth.models import Subject
from app.auth.utils import decode_subject_token

bearer_scheme = HTTPBearer(
    scheme_name="Bearer Authentication",
    description="Enter your JWT token",
    auto_error=False,
)


def get_current_subject(
    authorization: Annotated[str | None, Header()] = None,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ] = None,
) -> Subject:
    """
    Extract and validate the current subject from the Authorization header.

    Expected format: "Bearer <token>"
    """

    if credentials:
        token = credentials.credentials
    elif authorization:
        parts = authorization.split(" ")
        if len(parts) != 2 or parts[0] != "Bearer":
            raise HTTPException(
                status_code=400,
                detail="Invalid Authorization header format",
            )
        token = parts[1]
    else:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header",
        )
    subject = decode_subject_token(token)

    if not subject:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )

    return subject


CurrentSubjectDep = Annotated[Subject, Depends(get_current_subject)]

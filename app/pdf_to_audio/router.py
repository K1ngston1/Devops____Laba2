import cbor2
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response

from app.shared.dependencies.db import PostgresRunnerDep
from app.auth.dependencies import CurrentSubjectDep
from app.auth.enums import AccessLevel
from app.auth.decorators import authorize
from app.audit.decorators import audit

from .dto import (
    UploadKeyResponse,
    ConvertResponse,
    ConversionStatusResponse,
)
from . import service as pdf_service

router = APIRouter()


@router.get("/upload-key")
@audit()
@authorize(AccessLevel.RESTRICTED)
async def read_upload_key(
    db: PostgresRunnerDep, subject: CurrentSubjectDep, request: Request
) -> UploadKeyResponse:
    try:
        result = pdf_service.generate_upload_key(user_id=subject.id, db=db)
        return UploadKeyResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate upload key: {str(e)}"
        )


@router.post("/execute")
@audit()
@authorize(AccessLevel.RESTRICTED)
async def execute_pdf_to_audio(
    db: PostgresRunnerDep,
    subject: CurrentSubjectDep,
    request: Request,
):
    try:
        raw = await request.body()
        data = cbor2.loads(raw)

        task_uuid = data.get("task_uuid")
        if not task_uuid:
            raise ValueError("task_uuid is required")

        result = pdf_service.convert_pdf_to_audio_bytes(
            cbor_data=data, user_id=subject.id, db=db, task_uuid=task_uuid
        )

        return ConvertResponse(**result)
    except (KeyError, cbor2.CBORDecodeError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid CBOR data: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"PDF to audio conversion failed: {str(e)}"
        )


@router.get("/conversion-status/{task_uuid}")
@audit()
@authorize(AccessLevel.RESTRICTED)
async def read_conversion_status(
    task_uuid: str,
    db: PostgresRunnerDep,
    subject: CurrentSubjectDep,
    request: Request,
) -> ConversionStatusResponse:
    try:
        result = pdf_service.get_conversion_status(
            task_uuid=task_uuid, user_id=subject.id
        )
        return ConversionStatusResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get conversion status: {str(e)}"
        )


@router.get("/converted-audio/{task_uuid}")
@audit()
@authorize(AccessLevel.RESTRICTED)
async def read_converted_audio(
    task_uuid: str,
    db: PostgresRunnerDep,
    subject: CurrentSubjectDep,
    request: Request,
):
    try:
        result = pdf_service.get_converted_audio(
            task_uuid=task_uuid, user_id=subject.id, db=db
        )
        return Response(content=cbor2.dumps(result), media_type="application/cbor")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get converted audio: {str(e)}"
        )

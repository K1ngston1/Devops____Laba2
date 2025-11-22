from pydantic import BaseModel, Field


class UploadKeyResponse(BaseModel):
    is_success: bool
    encrypted_aes_key: str | None = None
    task_uuid: str | None = None


class PdfToAudioRequest(BaseModel):
    encrypted_file: bytes
    speed: int = Field(default=140, ge=80, le=300)


class PdfToAudioResponse(BaseModel):
    encrypted_audio: bytes
    encrypted_audio_key: bytes


class ConvertResponse(BaseModel):
    is_success: bool


class ConversionStatusResponse(BaseModel):
    is_done: bool
    has_error: bool = False
    error_message: str | None = None
    encrypted_aes_key: str | None = None


class ConvertedAudioResponse(BaseModel):
    encrypted_audio: bytes
    encrypted_audio_key: bytes

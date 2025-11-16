from pydantic import BaseModel, Field


class UploadKeyResponse(BaseModel):
    encrypted_aes_key: str


class PdfToAudioRequest(BaseModel):
    encrypted_file: bytes
    encrypted_aes_key: bytes
    speed: int = Field(default=140, ge=80, le=300)


class PdfToAudioResponse(BaseModel):
    encrypted_audio: bytes
    encrypted_audio_key: bytes

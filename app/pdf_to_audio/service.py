import subprocess
import base64
import fitz  # type: ignore
from langdetect import detect  # type: ignore

from app.shared.utils.db import SqlRunner
from app.shared.utils.crypto import (
    generate_aes_key,
    encrypt_with_aes,
    decrypt_with_aes,
    encrypt_with_ed25519_public_key,
    decrypt_with_ed25519_private_key,
)
from app.shared.utils.cbor import ensure_cbor_bytes
from app.credentials.service import load_server_private_key


def generate_upload_key(*, user_id: int, db: SqlRunner) -> dict[str, str]:
    user_public_key_row = (
        db.query("""
        SELECT public_key
        FROM users
        WHERE id = :user_id
    """)
        .bind(user_id=user_id)
        .first_row()
    )

    if not user_public_key_row or not user_public_key_row["public_key"]:
        raise ValueError("User public key not found in database")

    user_public_key_bytes = bytes(user_public_key_row["public_key"])
    aes_key = generate_aes_key()
    encrypted_aes_key = encrypt_with_ed25519_public_key(aes_key, user_public_key_bytes)

    return {"encrypted_aes_key": base64.b64encode(encrypted_aes_key).decode("utf-8")}


def convert_pdf_to_audio_bytes(
    *, cbor_data: dict, user_id: int, db: SqlRunner
) -> dict[str, bytes]:
    server_private_key = load_server_private_key(db=db)

    encrypted_file_bytes = ensure_cbor_bytes(
        cbor_data["encrypted_file"], "encrypted_file"
    )
    encrypted_aes_key_bytes = ensure_cbor_bytes(
        cbor_data["encrypted_aes_key"], "encrypted_aes_key"
    )
    speed = int(cbor_data.get("speed", 140))

    aes_key = decrypt_with_ed25519_private_key(
        encrypted_aes_key_bytes, server_private_key
    )
    pdf_bytes = decrypt_with_aes(encrypted_file_bytes, aes_key)
    text = extract_text_from_pdf(pdf_bytes)

    if not text.strip():
        raise ValueError("No text found in PDF or PDF is empty")

    audio_bytes = convert_text_to_audio(text, speed=speed)
    audio_aes_key = generate_aes_key()
    encrypted_audio = encrypt_with_aes(audio_bytes, audio_aes_key)

    user_public_key_row = (
        db.query("""
        SELECT public_key
        FROM users
        WHERE id = :user_id
    """)
        .bind(user_id=user_id)
        .first_row()
    )

    if not user_public_key_row or not user_public_key_row["public_key"]:
        raise ValueError("User public key not found in database")

    user_public_key_bytes = bytes(user_public_key_row["public_key"])
    encrypted_audio_aes_key = encrypt_with_ed25519_public_key(
        audio_aes_key, user_public_key_bytes
    )

    return {
        "encrypted_audio": encrypted_audio,
        "encrypted_audio_key": encrypted_audio_aes_key,
    }


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text_parts = []

    for page in doc:
        text_parts.append(page.get_text())
    doc.close()

    return "".join(text_parts)


def _detect_language(text: str) -> str:
    try:
        if not text or len(text.strip()) < 10:
            return "en"
        lang = detect(text)
        return str(lang)
    except Exception:
        return "en"


def _espeak_voice_for_lang(lang: str) -> str:
    if lang == "uk":
        return "uk"
    return "en-us"


def convert_text_to_audio(text: str, speed: int = 140) -> bytes:
    lang = _detect_language(text)
    espeak_voice = _espeak_voice_for_lang(lang)

    cmd = [
        "espeak-ng",
        "--stdout",
        "-v",
        espeak_voice,
        "-s",
        str(speed),
        text,
    ]
    try:
        proc = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
        )
        return proc.stdout
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Text-to-speech conversion failed: {e}")

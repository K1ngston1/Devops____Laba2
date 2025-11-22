import subprocess
import base64
import uuid
import threading
import fitz  # type: ignore
from langdetect import detect  # type: ignore

from app.shared.utils.db import SqlRunner
from app.shared.utils.crypto import (
    generate_aes_key,
    encrypt_with_aes,
    decrypt_with_aes,
    encrypt_with_ed25519_public_key,
)
from app.shared.utils.cbor import ensure_cbor_bytes

is_converter_busy = False
conversion_tasks: dict[str, dict] = {}
converter_lock = threading.Lock()


def generate_upload_key(*, user_id: int, db: SqlRunner) -> dict:
    global is_converter_busy, conversion_tasks

    with converter_lock:
        if is_converter_busy:
            return {"is_success": False}

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
        encrypted_aes_key = encrypt_with_ed25519_public_key(
            aes_key, user_public_key_bytes
        )

        task_uuid = str(uuid.uuid4())
        conversion_tasks[task_uuid] = {
            "aes_key": aes_key,
            "is_done": False,
            "user_id": user_id,
        }

        return {
            "is_success": True,
            "encrypted_aes_key": base64.b64encode(encrypted_aes_key).decode("utf-8"),
            "task_uuid": task_uuid,
        }


def convert_pdf_to_audio_bytes(
    *, cbor_data: dict, user_id: int, db: SqlRunner, task_uuid: str
) -> dict:
    global is_converter_busy, conversion_tasks

    with converter_lock:
        if task_uuid not in conversion_tasks:
            return {"is_success": False}

        if is_converter_busy:
            return {"is_success": False}

        aes_key = conversion_tasks[task_uuid]["aes_key"]

        is_converter_busy = True

    def conversion_worker():
        global is_converter_busy
        try:
            encrypted_file_bytes = ensure_cbor_bytes(
                cbor_data["encrypted_file"], "encrypted_file"
            )
            speed = int(cbor_data.get("speed", 140))

            pdf_bytes = decrypt_with_aes(encrypted_file_bytes, aes_key)
            text = extract_text_from_pdf(pdf_bytes)

            if not text.strip():
                raise ValueError("No text found in PDF or PDF is empty")

            audio_bytes = convert_text_to_audio(text, speed=speed)
            audio_aes_key = generate_aes_key()
            encrypted_audio = encrypt_with_aes(audio_bytes, audio_aes_key)

            db.query("""
                INSERT INTO conversions (uuid, encrypted_content)
                VALUES (:uuid, :encrypted_content)
            """).bind(uuid=task_uuid, encrypted_content=encrypted_audio).execute()

            with converter_lock:
                if task_uuid in conversion_tasks:
                    conversion_tasks[task_uuid]["audio_aes_key"] = audio_aes_key
                    conversion_tasks[task_uuid]["is_done"] = True

        except Exception as e:
            with converter_lock:
                if task_uuid in conversion_tasks:
                    conversion_tasks[task_uuid]["is_done"] = True
                    conversion_tasks[task_uuid]["error"] = str(e)
        finally:
            with converter_lock:
                is_converter_busy = False

    thread = threading.Thread(target=conversion_worker, daemon=True)
    thread.start()

    return {"is_success": True}


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


def get_conversion_status(*, task_uuid: str, user_id: int) -> dict:
    global conversion_tasks

    with converter_lock:
        if task_uuid not in conversion_tasks:
            raise ValueError("Task UUID not found")

        task = conversion_tasks[task_uuid]

        if task["user_id"] != user_id:
            raise ValueError("Unauthorized access to task")

        return {
            "is_done": task["is_done"],
            "encrypted_aes_key": None,
        }


def get_converted_audio(*, task_uuid: str, user_id: int, db: SqlRunner) -> dict:
    global conversion_tasks

    with converter_lock:
        if task_uuid not in conversion_tasks:
            raise ValueError("Task UUID not found")

        task = conversion_tasks[task_uuid]

        if not task["is_done"]:
            raise ValueError("Conversion not yet complete")

        if "error" in task:
            raise ValueError(f"Conversion failed: {task['error']}")

        if task["user_id"] != user_id:
            raise ValueError("Unauthorized access to task")

        audio_aes_key = task.get("audio_aes_key")
        if not audio_aes_key:
            raise ValueError("Audio key not found")

    # Fetch from database
    result = (
        db.query("""
        SELECT encrypted_content
        FROM conversions
        WHERE uuid = :uuid
    """)
        .bind(uuid=task_uuid)
        .first_row()
    )

    if not result:
        raise ValueError("Converted audio not found in database")

    encrypted_audio = bytes(result["encrypted_content"])

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

    db.query("""
        DELETE FROM conversions
        WHERE uuid = :uuid
    """).bind(uuid=task_uuid).execute()

    with converter_lock:
        if task_uuid in conversion_tasks:
            del conversion_tasks[task_uuid]

    return {
        "encrypted_audio": encrypted_audio,
        "encrypted_audio_key": encrypted_audio_aes_key,
    }

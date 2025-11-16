from typing import Any


def ensure_cbor_bytes(value: Any, field_name: str) -> bytes:
    """Ensure CBOR payload fields that represent binary data stay bytes."""

    if isinstance(value, bytes):
        return value
    if isinstance(value, bytearray):
        return bytes(value)
    if isinstance(value, memoryview):
        return value.tobytes()
    raise ValueError(
        f"{field_name} must be provided as bytes when using CBOR payloads."
    )

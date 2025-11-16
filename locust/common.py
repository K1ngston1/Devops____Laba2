"""
HMP Load Testing - Common Utilities

This module provides shared functions for all Locust test scripts:
- Ed25519 signature generation for authentication
- Auth flow (challenge + login)
- User flows (student and instructor)
- Test data loading
"""

import base64
import json
import random
from pathlib import Path
from typing import Optional
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def sign_challenge(challenge_b64: str, private_key_hex: str) -> str:
    """
    Sign a challenge using Ed25519 private key

    Args:
        challenge_b64: Base64 encoded challenge
        private_key_hex: Hex encoded private key (64 chars)

    Returns:
        Base64 encoded signature
    """
    challenge_bytes = base64.b64decode(challenge_b64)
    private_key_bytes = bytes.fromhex(private_key_hex)

    private_key = Ed25519PrivateKey.from_private_bytes(private_key_bytes)
    signature = private_key.sign(challenge_bytes)

    return base64.b64encode(signature).decode("utf-8")


def authenticate(client, user_id: int, private_key_hex: str) -> Optional[str]:
    """
    Perform authentication flow (challenge + login)

    Args:
        client: Locust HttpUser client
        user_id: User ID
        private_key_hex: Private key in hex format

    Returns:
        JWT token or None if authentication failed
    """
    # Step 1: Get challenge
    with client.post(
        "/auth/challenge",
        json={"user_id": user_id},
        catch_response=True,
        name="/auth/challenge",
    ) as response:
        if response.status_code != 200:
            response.failure(f"Challenge failed: {response.status_code}")
            return None

        challenge = response.json()["challenge"]

    # Step 2: Sign challenge
    signature = sign_challenge(challenge, private_key_hex)

    # Step 3: Login with signature
    with client.post(
        "/auth/login",
        json={"user_id": user_id, "challenge": challenge, "signature": signature},
        catch_response=True,
        name="/auth/login",
    ) as response:
        if response.status_code != 200:
            response.failure(f"Login failed: {response.status_code}")
            return None

        return response.json()["token"]


def load_test_data(filepath: str) -> dict:
    """
    Load test data from JSON file created by /admin/load-test/up endpoint

    Args:
        filepath: Path to JSON file with test data

    Returns:
        Dictionary with students, instructors, and projects
    """
    with open(filepath, "r") as f:
        return json.load(f)


def get_random_submission_file() -> bytes:
    """
    Load a random submission PDF file from data/submissions directory

    Returns:
        Binary content of a random PDF file
    """
    submissions_dir = Path(__file__).parent / "data" / "submissions"
    pdf_files = list(submissions_dir.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError("No PDF files found in data/submissions directory")

    selected_file = random.choice(pdf_files)
    with open(selected_file, "rb") as f:
        return f.read()

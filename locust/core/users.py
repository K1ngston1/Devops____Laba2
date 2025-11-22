"""
HMP Load Testing - User Behaviors

Defines student and instructor user behaviors for load testing.
User classes can be customized by setting weight and wait_time attributes.
"""

import random
import base64
import cbor2
from locust import HttpUser, task, between, events  # type: ignore[attr-defined]

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from common import authenticate, load_test_data, get_random_submission_file  # type: ignore[import-not-found]


TEST_DATA = None


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    global TEST_DATA
    TEST_DATA = load_test_data("data/test_data.json")


class BaseUser(HttpUser):
    """Base class with token refresh capability"""

    abstract = True

    def refresh_token(self):
        """Re-authenticate to get a fresh token"""
        self.token = authenticate(
            self.client, self.user_data["id"], self.user_data["private_key"]
        )
        if not self.token:
            raise Exception(f"Re-authentication failed for user {self.user_data['id']}")
        self.headers["Authorization"] = f"Bearer {self.token}"

    def get_headers(self, content_type="application/json"):
        """Get current headers with fresh token"""
        return {"Authorization": f"Bearer {self.token}", "Content-Type": content_type}

    def make_request(self, method, url, **kwargs):
        """Make HTTP request with automatic token refresh on 401"""
        name = kwargs.pop("name", url)

        # Ensure we use current token
        if "headers" not in kwargs:
            kwargs["headers"] = self.headers

        with self.client.request(
            method, url, name=name, catch_response=True, **kwargs
        ) as response:
            if response.status_code == 401:
                response.failure("Token expired, refreshing...")
                self.refresh_token()

                # Update headers with new token
                if "headers" in kwargs:
                    kwargs["headers"]["Authorization"] = f"Bearer {self.token}"

                with self.client.request(
                    method, url, name=f"{name} [retry]", catch_response=True, **kwargs
                ) as retry_response:
                    if retry_response.status_code >= 400:
                        retry_response.failure(
                            f"Request failed after token refresh: {retry_response.status_code}"
                        )
                    else:
                        retry_response.success()
                    return retry_response
            elif response.status_code >= 400:
                response.failure(f"Request failed: {response.status_code}")
            else:
                response.success()
            return response


class BaseStudentUser(BaseUser):
    """
    Base student user behavior.
    Override weight and wait_time in subclasses for different scenarios.
    """

    abstract = True

    def on_start(self):
        student = random.choice(TEST_DATA["students"])
        self.user_data = student

        self.token = authenticate(self.client, student["id"], student["private_key"])
        if not self.token:
            raise Exception(f"Authentication failed for student {student['id']}")

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    @task(10)
    def list_projects(self):
        self.make_request("GET", "/project/", name="/project/ [list]")

    @task(5)
    def view_project_details(self):
        if self.user_data["project_ids"]:
            project_id = random.choice(self.user_data["project_ids"])
            self.make_request(
                "GET", f"/project/{project_id}", name="/project/{id} [detail]"
            )

    @task(1)
    def submit_assignment(self):
        if self.user_data["project_ids"]:
            project_id = random.choice(self.user_data["project_ids"])
            submission_data = {
                "project_id": project_id,
                "title": f"Load Test from {self.user_data['email']}",
                "encrypted_content": get_random_submission_file(),
            }
            self.make_request(
                "POST",
                "/submission/",
                data=cbor2.dumps(submission_data),
                headers=self.get_headers("application/cbor"),
                name="/submission/ [create]",
            )


class BaseInstructorUser(BaseUser):
    """
    Base instructor user behavior.
    Override weight and wait_time in subclasses for different scenarios.
    """

    abstract = True

    def on_start(self):
        instructor = random.choice(TEST_DATA["instructors"])
        self.user_data = instructor

        self.token = authenticate(
            self.client, instructor["id"], instructor["private_key"]
        )
        if not self.token:
            raise Exception(f"Authentication failed for instructor {instructor['id']}")

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    @task(8)
    def list_projects(self):
        self.make_request("GET", "/project/", name="/project/ [list]")

    @task(5)
    def view_project_details(self):
        if self.user_data["project_ids"]:
            project_id = random.choice(self.user_data["project_ids"])
            self.make_request(
                "GET", f"/project/{project_id}", name="/project/{id} [detail]"
            )

    @task(10)
    def list_submissions(self):
        self.make_request("GET", "/submission/", name="/submission/ [list]")

    @task(3)
    def download_submission(self):
        response = self.make_request(
            "GET", "/submission/", name="/submission/ [list for download]"
        )
        if response.status_code == 200:
            try:
                submissions = response.json()
                if submissions:
                    submission = random.choice(submissions[:10])
                    self.make_request(
                        "GET",
                        f"/submission/{submission['id']}/content",
                        name="/submission/{id}/content [download]",
                    )
            except Exception:
                pass

    @task(1)
    def convert_to_audio(self):
        import time

        upload_key_response = self.make_request(
            "GET", "/pdf-to-audio/upload-key", name="/pdf-to-audio/upload-key [get]"
        )
        if upload_key_response.status_code != 200:
            return

        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import (
                Ed25519PrivateKey,
            )
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            from cryptography.hazmat.primitives import hashes
            import secrets

            upload_key_data = upload_key_response.json()
            is_success = upload_key_data.get("is_success")

            if not is_success:
                return

            encrypted_aes_key_b64 = upload_key_data.get("encrypted_aes_key")
            task_uuid = upload_key_data.get("task_uuid")

            if not encrypted_aes_key_b64 or not task_uuid:
                return

            instructor_private_key = Ed25519PrivateKey.from_private_bytes(
                bytes.fromhex(self.user_data["private_key"])
            )
            instructor_public_key_bytes = (
                instructor_private_key.public_key().public_bytes_raw()
            )

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=instructor_public_key_bytes[:16],
                iterations=65536,
                backend=default_backend(),
            )
            derived_key = kdf.derive(instructor_public_key_bytes)

            encrypted_aes_key = base64.b64decode(encrypted_aes_key_b64)
            if len(encrypted_aes_key) < 12 + 16:
                return

            iv = encrypted_aes_key[:12]
            tag = encrypted_aes_key[-16:]
            ciphertext = encrypted_aes_key[12:-16]

            decryptor = Cipher(
                algorithms.AES(derived_key),
                modes.GCM(iv, tag),
                backend=default_backend(),
            ).decryptor()
            aes_key = decryptor.update(ciphertext) + decryptor.finalize()

            pdf_content = get_random_submission_file()

            iv_pdf = secrets.token_bytes(12)
            encryptor = Cipher(
                algorithms.AES(aes_key), modes.GCM(iv_pdf), backend=default_backend()
            ).encryptor()
            ciphertext_pdf = encryptor.update(pdf_content) + encryptor.finalize()
            encrypted_pdf = iv_pdf + ciphertext_pdf + encryptor.tag

            conversion_data = {
                "encrypted_file": encrypted_pdf,
                "speed": 140,
                "task_uuid": task_uuid,
            }

            trigger_response = self.make_request(
                "POST",
                "/pdf-to-audio/execute",
                data=cbor2.dumps(conversion_data),
                headers=self.get_headers("application/cbor"),
                name="/pdf-to-audio/execute [trigger]",
            )

            if trigger_response.status_code != 200:
                return

            trigger_data = trigger_response.json()
            if not trigger_data.get("is_success"):
                return

            max_attempts = 24
            for attempt in range(max_attempts):
                time.sleep(5)

                status_response = self.make_request(
                    "GET",
                    f"/pdf-to-audio/conversion-status/{task_uuid}",
                    name="/pdf-to-audio/conversion-status [poll]",
                )

                if status_response.status_code != 200:
                    break

                status_data = status_response.json()
                if status_data.get("is_done"):
                    audio_response = self.make_request(
                        "GET",
                        f"/pdf-to-audio/converted-audio/{task_uuid}",
                        name="/pdf-to-audio/converted-audio [download]",
                    )

                    if audio_response.status_code == 200:
                        break

        except Exception:
            pass


class StudentUser(BaseStudentUser):
    """Standard student behavior: 80% of users, normal think time"""

    weight = 80
    wait_time = between(5, 15)


class InstructorUser(BaseInstructorUser):
    """Standard instructor behavior: 20% of users, normal think time"""

    weight = 20
    wait_time = between(5, 15)


class SpikeStudentUser(BaseStudentUser):
    """Deadline rush student behavior: 95% of users, faster submissions"""

    weight = 95
    wait_time = between(2, 8)

    @task(5)
    def list_projects(self):
        self.make_request("GET", "/project/", name="/project/ [list]")

    @task(3)
    def view_project_details(self):
        if self.user_data["project_ids"]:
            project_id = random.choice(self.user_data["project_ids"])
            self.make_request(
                "GET", f"/project/{project_id}", name="/project/{id} [detail]"
            )

    @task(10)
    def submit_assignment(self):
        if self.user_data["project_ids"]:
            project_id = random.choice(self.user_data["project_ids"])
            submission_data = {
                "project_id": project_id,
                "title": f"Spike Test from {self.user_data['email']}",
                "encrypted_content": get_random_submission_file(),
            }
            self.make_request(
                "POST",
                "/submission/",
                data=cbor2.dumps(submission_data),
                headers=self.get_headers("application/cbor"),
                name="/submission/ [create]",
            )


class SpikeInstructorUser(BaseInstructorUser):
    """Deadline rush instructor behavior: 5% of users, monitoring submissions"""

    weight = 5
    wait_time = between(5, 10)

    @task(10)
    def list_submissions(self):
        self.make_request("GET", "/submission/", name="/submission/ [list]")

    @task(5)
    def download_submission(self):
        response = self.make_request(
            "GET", "/submission/", name="/submission/ [list for download]"
        )
        if response.status_code == 200:
            try:
                submissions = response.json()
                if submissions:
                    submission = random.choice(submissions[:10])
                    self.make_request(
                        "GET",
                        f"/submission/{submission['id']}/content",
                        name="/submission/{id}/content [download]",
                    )
            except Exception:
                pass

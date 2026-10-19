from cryptography.hazmat.primitives import serialization

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import base64
import json


def load_private_key():
    with open("keys/LOGIN_PRIVATE_KEY.pem", "rb") as f:
        private_key_data = f.read()

    private_key = serialization.load_pem_private_key(
        private_key_data,
        password=None
    )
    return private_key



def decrypt_login_payload(payload_b64: str):
    private_key = load_private_key()

    encrypted_bytes = base64.b64decode(payload_b64)

    decrypted = private_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return json.loads(decrypted.decode("utf-8"))

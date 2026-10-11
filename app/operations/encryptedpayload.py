import base64
import os

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class EncryptedPayload(BaseModel):
    iv: str
    payload: str

# Colocar con .env para no romper la logica



AES_KEY_P = os.getenv("AES_KEY_BASE64")

AES_KEY = base64.b64decode(AES_KEY_P)
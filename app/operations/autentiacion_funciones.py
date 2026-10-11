
import os


from dotenv import load_dotenv
from fastapi import Cookie, HTTPException, Request
from fastapi import status
from fastapi.params import Depends
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select

from app.operations.token_manager import TokenManager
from db import SessionDep
from models import UserTable, Usuario, UsuarioCreate
from password import verify_password_f
from pathlib import Path
from dotenv import load_dotenv



def get_token_manager():
    return TokenManager(secret_key=SECRET_KEY)

# env_path = Path(__file__).resolve().parent / ".env"
# load_dotenv(dotenv_path=env_pathç)
load_dotenv()



SECRET_KEY = os.getenv("SECRET_KEY")
# SECRET_KEY = "clave_secreta"
TIME_EXPIRE = 60 * 45 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(
    session: SessionDep,
    email: str,
    password: str
) -> UserTable:
    try:
        
        user_db = session.exec(select(UserTable).where(UserTable.email == email)).first()
        if not user_db:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
        
        hass_entrada = password

        if not verify_password_f(hass_entrada,user_db.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Contraseña incorrecta")

        return user_db

    except Exception as e:
        print("Error al conectar o verificar usuario:", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno del servidor {e}")


def get_current_session_user(
    session: SessionDep,
    request: Request,
    token_manager: TokenManager = Depends(get_token_manager),

):
    token = request.cookies.get("access_token")
    user_id = request.cookies.get("user_id")

    if not token or not user_id:
        return RedirectResponse("/", status_code=302)

    try:
        payload = token_manager.decode_token(token)
        user_db = session.get(UserTable, int(user_id))

        if not user_db:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")

        return user_db

    except Exception:
        return RedirectResponse("/", status_code=302)


def get_current_user_id(
    session: SessionDep,
    user_cookie_id: str | None = Cookie(alias="user_id", default=None)
) -> UserTable:


    if not user_cookie_id:
        return None

    user = session.get(UserTable, int(user_cookie_id))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inválido"
        )

    return user


def get_current_user_middle(request:Request):
    user = getattr(request.state, "user", None)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado"
        )

    return user
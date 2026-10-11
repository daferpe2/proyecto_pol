from typing import Annotated

from fastapi import status
from fastapi.responses import RedirectResponse


def access_token_m(access_token):
    if access_token is None:
        return RedirectResponse(url="/inicio_secion",status_code=status.HTTP_302_FOUND)
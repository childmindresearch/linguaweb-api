"""Security module for the CTK API."""

import fastapi
from fastapi import security, status

from linguaweb_api.core import config

settings = config.get_settings()
API_KEY = settings.API_KEY


def check_api_key(
    api_key_header: str = fastapi.Security(security.APIKeyHeader(name="x-api-key")),
) -> None:
    """Checks the validity of the API key provided in the API key header.

    At present, only a single API key is supported and is stored in the environment.

    Args:
        api_key_header: The API key provided in the API key header.

    Raises:
        fastapi.HTTPException: 401 If the API key is invalid or missing.

    """
    if api_key_header == API_KEY.get_secret_value():
        return
    raise fastapi.HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key.",
    )

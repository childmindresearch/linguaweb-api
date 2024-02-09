"""Controller to assess the health of the services."""
import fastapi
import requests
from fastapi import status


def get_api_health() -> None:
    """Returns the health of the API."""


def get_internet_connectivity() -> None:
    """Checks the internet connectivity of the API."""
    response = requests.get("https://www.google.com", timeout=5)
    if response.status_code != status.HTTP_200_OK:
        raise fastapi.HTTPException(
            status_code=response.status_code,
            detail="Internet connectivity check failed.",
        )

"""Tests for the health endpoints."""

from fastapi import status, testclient

from tests.endpoint import conftest


def test_get_health(
    client: testclient.TestClient,
    endpoints: conftest.Endpoints,
) -> None:
    """Tests the get health endpoint."""
    response = client.get(endpoints.GET_HEALTH)

    assert response.status_code == status.HTTP_200_OK


def test_get_connectivity(
    client: testclient.TestClient,
    endpoints: conftest.Endpoints,
) -> None:
    """Tests the get connectivity endpoint."""
    response = client.get(endpoints.GET_CONNECTIVITY)

    assert response.status_code == status.HTTP_200_OK

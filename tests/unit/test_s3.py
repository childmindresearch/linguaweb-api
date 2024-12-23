"""Unit tests for the S3 client."""

import moto
import pytest
from botocore import errorfactory

from linguaweb_api.microservices import s3


@moto.mock_s3
def test_s3_create() -> None:
    """Test that an object is created in the bucket."""
    test_key = "test_key"
    test_data = b"test_data"
    client = s3.S3()

    client.create(test_key, test_data)

    stored_data = client.read(test_key)
    assert stored_data == test_data


@moto.mock_s3
def test_s3_read_nonexistent_key() -> None:
    """Test that reading a nonexistent key raises an exception."""
    client = s3.S3()
    test_key = "nonexistent_key"

    with pytest.raises(errorfactory.ClientError):
        client.read(test_key)


@moto.mock_s3
def test__is_existing_bucket() -> None:
    """Test that the bucket exists."""
    client = s3.S3()

    assert client._is_existing_bucket(s3.S3_BUCKET_NAME)
    assert not client._is_existing_bucket("nonexistent_bucket")

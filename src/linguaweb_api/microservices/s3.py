"""Interactions with an S3/MinIO bucket."""

import logging

import boto3
from botocore import errorfactory

from linguaweb_api.core import config

settings = config.get_settings()
S3_BUCKET_NAME = settings.S3_BUCKET_NAME
S3_ENDPOINT_URL = settings.S3_ENDPOINT_URL
S3_ACCESS_KEY = settings.S3_ACCESS_KEY
S3_SECRET_KEY = settings.S3_SECRET_KEY
S3_REGION = settings.S3_REGION
LOGGER_NAME = settings.LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


class S3:
    """Client for interacting with an S3/MinIO bucket.

    Attributes:
        s3: The S3 resource.
        bucket: The bucket.
    """

    def __init__(self) -> None:
        """Initializes a new instance of the S3 class.

        Args:
            bucket_name: The name of the bucket.
        """
        logger.debug("Connecting to S3 at: %s", S3_ENDPOINT_URL)
        self.s3 = boto3.resource(
            "s3",
            region_name=S3_REGION,
            endpoint_url=S3_ENDPOINT_URL,
            aws_access_key_id=S3_ACCESS_KEY.get_secret_value(),
            aws_secret_access_key=S3_SECRET_KEY.get_secret_value(),
        )

        if self._is_existing_bucket(S3_BUCKET_NAME):
            self.bucket = self.s3.Bucket(S3_BUCKET_NAME)
        else:
            self.bucket = self.s3.create_bucket(Bucket=S3_BUCKET_NAME)

    def create(self, key: str, data: bytes) -> None:
        """Creates an object in the bucket.

        Args:
            key: The key of the object.
            data: The data to store in the object.
        """
        self.bucket.put_object(Key=key, Body=data)

    def read(self, key: str) -> bytes:
        """Reads an object from the bucket.

        Args:
            key: The key of the object.
        """
        return self.bucket.Object(key).get()["Body"].read()

    def _is_existing_bucket(self, bucket_name: str) -> bool:
        """Ensure that the bucket exists, and if not, create it."""
        try:
            self.s3.meta.client.head_bucket(Bucket=bucket_name)
        except errorfactory.ClientError:
            return False
        else:
            return True

"""Creates the handler for AWS Lambda."""  # noqa: INP001
import mangum

from linguaweb_api import main

handler = mangum.Mangum(main.app)

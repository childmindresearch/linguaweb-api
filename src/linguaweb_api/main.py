"""Entrypoint for the API."""
import logging

import fastapi
from fastapi import responses
from fastapi.middleware import cors

from linguaweb_api.core import config, middleware
from linguaweb_api.microservices import sql
from linguaweb_api.routers.admin import views as admin_views
from linguaweb_api.routers.health import views as health_views
from linguaweb_api.routers.speech import views as speech_views
from linguaweb_api.routers.words import views as words_views

settings = config.get_settings()
LOGGER_NAME = settings.LOGGER_NAME

config.initialize_logger()
logger = logging.getLogger(LOGGER_NAME)


logger.info("Starting API.")
app = fastapi.FastAPI(
    title="LinguaWeb API",
    version="0.0.2",
    contact={
        "name": "Center for Data Analytics, Innovation, and Rigor",
        "url": "https://github.com/childmindresearch/",
        "email": "dair@childmind.org",
    },
    swagger_ui_parameters={"operationsSorter": "method"},
    openapi_tags=config.open_api_specification(),  # type: ignore[arg-type] # Our class is more specific.
)


@app.get("/")
async def direct_to_docs() -> responses.RedirectResponse:
    """Redirects to the API documentation."""
    return responses.RedirectResponse("/docs")


logger.info("Initializing API routes.")
base_router = fastapi.APIRouter(prefix="/api/v1")
base_router.include_router(admin_views.router)
base_router.include_router(health_views.router)
base_router.include_router(speech_views.router)
base_router.include_router(words_views.router)
app.include_router(base_router)

logger.info("Initializing microservices.")
logger.debug("Initializing SQL microservice.")
database = sql.Database()
database.create_database()

logger.info("Adding middleware.")
logger.debug("Adding CORS middleware.")
app.add_middleware(
    cors.CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.debug("Adding request logger middleware.")
app.add_middleware(middleware.RequestLoggerMiddleware)

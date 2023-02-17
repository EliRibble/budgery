"Module for the FastAPI application."
import logging

from budgery.db import connection as db_connection
from budgery.main import app

LOGGER = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)
@app.on_event("startup")
def startup() -> None:
	LOGGER.info("Startup for main app.")
	#apply_migrations(str(BaseMeta.database.url))
	#if not BaseMeta.database.is_connected:
		#await BaseMeta.database.connect()

@app.on_event("shutdown")
def shutdown() -> None:
	LOGGER.info("Shutdown for main app.")

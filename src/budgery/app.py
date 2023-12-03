"Module for the FastAPI application."
from contextlib import asynccontextmanager
import logging

from budgery.db import connection as db_connection
from budgery.main import app

logging.basicConfig(level=logging.INFO)

import logging
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from starlette.config import Config

from budgery.db.history_meta import versioned_session

LOGGER = logging.getLogger(__name__)

def connect(config: Config):
	url = config("SQL_ALCHEMY_DATABASE_URL", default="sqlite:///./budgery.db")
	LOGGER.info("Connecting to DB at %s", url)
	return create_engine(
		url,
		connect_args={"check_same_thread": False},
	)

def session(engine):
	maker = sessionmaker(autocommit=False, autoflush=False, bind=engine)
	versioned_session(maker)
	return maker()

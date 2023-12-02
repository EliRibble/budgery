from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from starlette.config import Config

from budgery.db.history_meta import versioned_session

def connect(config: Config):
	return create_engine(
		config("SQL_ALCHEMY_DATABASE_URL", default="sqlite:///./budgery.db"),
		connect_args={"check_same_thread": False},
	)

def session(engine):
	maker = sessionmaker(autocommit=False, autoflush=False, bind=engine)
	versioned_session(maker)
	return maker()

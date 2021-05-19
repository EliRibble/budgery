from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from starlette.config import Config

def connect(config: Config):
	return create_engine(
		config("SQL_ALCHEMY_DATABASE_URL", default="sqlite:///./budgery.db"),
		connect_args={"check_same_thread": False},
	)

def session(engine):
	return sessionmaker(autocommit=False, autoflush=False, bind=engine)()

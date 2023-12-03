from pytest_alembic.config import Config

import pytest
import sqlalchemy

@pytest.fixture
def alembic_config():
	"""Override this fixture to configure the exact alembic context setup required.
	"""
	config = Config()
	return config

@pytest.fixture
def alembic_engine(alembic_config):
    """Override this fixture to provide pytest-alembic powered tests with a database handle.
    """
    return sqlalchemy.create_engine("sqlite:///./budgery-test.db")

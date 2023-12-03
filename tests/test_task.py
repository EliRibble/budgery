import csv
import datetime
import logging
from pathlib import Path
import pprint
from typing import Dict, List
import unittest

from fastapi.testclient import TestClient
from starlette.config import Config

from budgery import task
from budgery.main import app, get_config
from budgery.db import crud, models
from budgery.db.connection import connect, Session
from budgery.db.models import Base
from budgery.user import User

LOGGER = logging.getLogger(__name__)

def _get_import_data(filename: str) -> List[Dict[str, str]]:
	"Get the content of a test import file."
	with open(Path("tests") / "import_data" / filename, "rb") as f:
		return task._extract_rows(f)

def test_everydollar_import():
	"Test that we can handle an import from Every Dollar."
	content = _get_import_data("every_dollar.csv")
	assert len(content) == 8
	assert content[0].sourcink_from == "America First Checking"
	assert content[0].at.year == 2021
	assert content[0].at.month == 4
	assert content[0].at.day == 24

def test_ally_import():
	content = _get_import_data("ally.csv")
	assert len(content) == 5
	assert content[0].description == "SMASHBURGER  1477 CHANDLER, AZ, USA"
	assert content[3].amount == -61.40

def test_america_first_credit_union():
	content = _get_import_data("afcu.csv")
	assert len(content), 31
	assert content[0].description == "PEER TO PEER TRANSFER S 866-224-2158;301400N0HYUG;2023-01-17;DR"
	assert content[10].amount == -100
	assert content[20].at == datetime.datetime(2023, 1, 4)

def test_american_express():
	content = _get_import_data("amex.xlsx")
	assert len(content) == 14
	assert content[0].at == datetime.datetime(2023, 1, 12)
	assert content[2].extended_details  == "NT_N9T78DMS +17198664578\nUSA SWIMMING, INC.\nCOLORADO SPRINGS\nCO\n+17198664578"
	assert content[3].category == "Business Services-Other Services"

class TestImport(unittest.IsolatedAsyncioTestCase):
	def setUp(self):
		logging.basicConfig(level=logging.INFO)
		config = Config("test.env")
		self.config = config
		def get_config_override() -> Config:
			return config
		app.dependency_overrides[get_config] = get_config_override
		engine = connect(config)
		Base.metadata.create_all(engine)
		self.db = Session(engine)

	async def test_import_amex_csv(self):
		filename = "tests/import_data/amex.xlsx"
		import_file = open(filename, "rb")
		user = User(
			auth_time=datetime.datetime.utcnow(),
			email=None,
			email_verified=False,
			expiration=datetime.datetime.utcnow() + datetime.timedelta(days=1),
			family_name="Tester",
			given_name="Robert",
			name="Bobby Tester",
			disabled=False,
			username="bobbytester",
		)
		db_user = crud.user_ensure_exists(self.db, user)
		assert db_user
		institution = crud.institution_create(
			db=self.db,
			user=db_user,
			aba_routing_number=0,
			name="test-institution",
		)
		account = crud.account_create(
			db=self.db,
			institution_id=institution.id,
			name="test-account",
			user=db_user,
		)
		import_job = crud.import_job_create(
			account_id=account.id,
			db=self.db,
			filename=filename,
			user=db_user,
		)
		await task.process_transaction_upload(
			import_file=import_file,
			db=self.db,
			filename=filename,
			import_job=import_job,
			user=user,
		)
		import_job = crud.import_job_get_by_id(
			db=self.db,
			user=db_user,
			import_job_id=import_job.id,
		)
		assert import_job.status == models.ImportJobStatus.finished

	def test_root(self):
		with TestClient(app) as client:
			response = client.get("/")
		assert response.status_code == 200

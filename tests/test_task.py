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
from budgery.db import connection as db_connection
from budgery.db import crud

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
		LOGGER.info("Doing setUp")
		def get_config_override() -> Config:
			return Config("test.env")
		app.dependency_overrides[get_config] = get_config_override
		#@app.on_event("startup")
		#def setup_for_tests() -> None:
			#LOGGER.info("Setup for tests")
			# create_database(db_url=db_url)
			# stamp_database(db_url=db_url)

	def test_root(self):
		with TestClient(app) as client:
			response = client.get("/")
		assert response.status_code == 200

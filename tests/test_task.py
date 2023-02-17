import csv
import datetime
from pathlib import Path
import pprint
from typing import Dict, List
import unittest

from budgery import task
from budgery.db import connection as db_connection
from budgery.db import crud
from starlette.config import Config, environ

class TestParsers(unittest.TestCase):
	def setUp(self):
		config = Config("test.env")
		db_engine = db_connection.connect(config)
		self.db = db_connection.session(db_engine)

	def _get_import_data(self, filename: str) -> List[Dict[str, str]]:
		"Get the content of a test import file."
		with open(Path("tests") / "import_data" / filename, "rb") as f:
			return task._extract_rows(f)

	def test_everydollar_import(self):
		"Test that we can handle an import from Every Dollar."
		content = self._get_import_data("every_dollar.csv")
		self.assertEqual(len(content), 8)
		self.assertEqual(content[0].sourcink_from, "America First Checking")
		self.assertEqual(content[0].at.year, 2021)
		self.assertEqual(content[0].at.month, 4)
		self.assertEqual(content[0].at.day, 24)

	def test_ally_import(self):
		content = self._get_import_data("ally.csv")
		self.assertEqual(len(content), 5)
		self.assertEqual(content[0].description, "SMASHBURGER  1477 CHANDLER, AZ, USA")
		self.assertEqual(content[3].amount, -61.40)

	def test_america_first_credit_union(self):
		content = self._get_import_data("afcu.csv")
		self.assertEqual(len(content), 31)
		self.assertEqual(content[0].description, "PEER TO PEER TRANSFER S 866-224-2158;301400N0HYUG;2023-01-17;DR")
		self.assertEqual(content[10].amount, -100)
		self.assertEqual(content[20].at, datetime.datetime(2023, 1, 4))

	def test_american_express(self):
		content = self._get_import_data("amex.xlsx")
		self.assertEqual(len(content), 14)
		self.assertEqual(content[0].at, datetime.datetime(2023, 1, 12))
		self.assertEqual(content[2].extended_details, "NT_N9T78DMS +17198664578\nUSA SWIMMING, INC.\nCOLORADO SPRINGS\nCO\n+17198664578")
		self.assertEqual(content[3].category, "Business Services-Other Services")

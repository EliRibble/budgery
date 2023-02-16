import csv
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
			header, reader = task._csv_iterator(f)
			processor = task._processor_from_header(header)
			return [d for d in task._clean_data_iterator(header, reader)]

	def test_everydollar_import(self):
		"Test that we can handle an import from Every Dollar."
		content = self._get_import_data("every_dollar.csv")
		self.assertEqual(len(content), 8)
		self.assertEqual(content[0]["source_name"], "America First Checking")
		self.assertEqual(content[0]["date"], "2021-04-24T00:00:00-06:00")

	def test_ally_import(self):
		content = self._get_import_data("ally.csv")
		self.assertEqual(len(content), 5)
		self.assertEqual(content[0]["Description"], "SMASHBURGER  1477 CHANDLER, AZ, USA")
		self.assertEqual(content[3]["Amount"], "-61.40")

	def test_america_first_credit_union(self):
		content = self._get_import_data("afcu.csv")
		self.assertEqual(len(content), 35)
		self.assertEqual(content[0]["Description"], "Pending - 01/13 - AMZN Mktp US")
		self.assertEqual(content[10]["Debit"], "-95.11")
		self.assertEqual(content[20]["Date"], "1/5/2023")

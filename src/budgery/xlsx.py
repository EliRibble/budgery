import datetime
import io
from typing import Iterable, List, Mapping, Optional, Tuple
import warnings

import openpyxl

from budgery.dataclasses import ImportRow

(
	"Date",
	"Description",
	"Card Member",
	"Account #",
	"Amount",
	"Extended Details",
	"Appears On Your Statement As",
	"Address",
	"City/State",
	"Zip Code",
	"Country",
	"Reference",
	"Category",
)

def _process_amex(data: Mapping[str, str]) -> Optional[ImportRow]:
	"Process a single row of Amex data."
	at = datetime.datetime.strptime(data["Date"], "%m/%d/%Y")
	return ImportRow(
		account_id_is_from=True,
		address=data["Address"],
		amount=data["Amount"],
		at=at,
		category=data["Category"],
		city=data["City/State"],
		description=data["Description"],
		extended_details=data["Extended Details"],
		sourcink_from=None,
		sourcink_to=None,
		zipcode=data["Zip Code"],
	)

def _xlsx_row_dict_iterator(headers, sheet_iterator):
	for row in sheet_iterator:
		yield {h: row[i].value for i, h in enumerate(headers)}


def extract_rows(content: bytes) -> List[ImportRow]:
	"Get all the content from the xlsx file"
	# There's no way to keep openpyxl from emitting warnings about the internal
	# mechanics of the file we are importing. This looks like
	# "Workbook contains no default style, apply openpyxl's default"
	with warnings.catch_warnings(record=True):
		warnings.simplefilter("always")
		workbook = openpyxl.load_workbook(io.BytesIO(content))
		sheet_names = workbook.get_sheet_names()
		# For now, assume AMEX
		# Amex spreadsheet has headers starting at row 7
		sheet = workbook.get_sheet_by_name("Transaction Details")
	itr = sheet.iter_rows()
	for i in range(6):
		next(itr)
	head_row = next(itr)
	headers = tuple(c.value for c in head_row)
	data = [_process_amex(row) for row in _xlsx_row_dict_iterator(headers, itr)]
	data = [d for d in data if d]
	return data

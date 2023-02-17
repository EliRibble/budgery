import datetime
import io
from typing import Iterable, List, Mapping, Optional, Tuple

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
	account_id_is_from = True
	amount = data["Amount"]
	at = datetime.datetime.strptime(data["Date"], "%m/%d/%Y")
	description = data["Description"]
	return ImportRow(
		account_id_is_from=account_id_is_from,
		amount=amount,
		at=at,
		category=None,
		description=description,
		sourcink_from=None,
		sourcink_to=None,
	)

def _xlsx_row_dict_iterator(headers, sheet_iterator):
	for row in sheet_iterator:
		yield {h: row[i].value for i, h in enumerate(headers)}


def extract_rows(content: bytes) -> List[ImportRow]:
	"Get all the content from the xlsx file"
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

import asyncio
import datetime
import logging
from pathlib import Path
import tempfile
from typing import List

import magic

from budgery.dataclasses import ImportRow
from budgery.db import crud
import budgery.csv
import budgery.xlsx

LOGGER = logging.getLogger(__name__)

def _extract_rows(f) -> List[ImportRow]:
	"Extract the rows from an import file."
	head = f.read(2048)
	detected = magic.from_buffer(head)
	parts = []
	while True:
		p = f.read(2048 * 8)
		if p:
			parts.append(p)
		break
	content = head + b''.join(parts)
	f.seek(0)
	
	if detected == "CSV text":
		return budgery.csv.extract_rows(content)
	elif detected == "Microsoft OOXML":
		return budgery.xlsx.extract_rows(content)
	else:
		raise Exception(f"No idea what to do with a '{detected}' file")

async def process_transaction_upload(
		import_file: tempfile.TemporaryFile,
		db,
		filename: str,
		import_job,
		user,
	) -> None:
	await asyncio.sleep(0)
	sourcink_unknown = crud.sourcink_get_or_create(db, "Unknown")
	type_ = data["Type"]
	if type_ == "Withdrawal":
		account_id_from = account_id
		account_id_to = None
	elif type_ == "Deposit":
		account_id_from = None
		account_id_to = account_id
	else:
		raise Exception(f"Unknown type {type_}")

	crud.transaction_create(
		db=db,
		description=description,
		account_id_from=account_id_from,
		account_id_to=account_id_to,
		amount=amount,
		at=at,
		category=None,
		import_job=import_job,
		sourcink_from=sourcink_unknown,
		sourcink_to=sourcink_unknown,
	)
	if filename.endswith(".csv"):
		header, reader = _csv_iterator(import_file)
	elif filename.endswith(".xlxs"):
		header, reader = _xlxs_iterator(import_file)
	processor = _processor_from_header(header)
	for data in _clean_data_iterator(header, reader):
		processor(
			account_id=import_job.account_id,
			data=data,
			db=db,
			import_job=import_job,
			user=user,
		)
	crud.import_job_finish(db, import_job)

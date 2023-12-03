import asyncio
import datetime
import logging
from pathlib import Path
import tempfile
from typing import IO, List

import magic

from budgery.dataclasses import ImportRow
from budgery.db import crud, models
from budgery.user import User
import budgery.csv
import budgery.xlsx

LOGGER = logging.getLogger(__name__)

def _extract_rows(f: IO) -> List[ImportRow]:
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
		import_file: IO,
		db: crud.Session,
		filename: str,
		import_job: models.ImportJob,
		user: User,
	) -> None:
	# Immediately push this coroutine to the bottom of the stack.
	await asyncio.sleep(0)
	rows = _extract_rows(import_file)
	sourcink_unknown = crud.sourcink_get_or_create(db, "Unknown")
	for row in rows:
		if row.account_id_is_from:
			account_id_from = import_job.account_id
			account_id_to = None
		else:
			account_id_from = None
			account_id_to = import_job.account_id
		crud.transaction_create(
			db=db,
			description=row.description,
			account_id_from=account_id_from,
			account_id_to=account_id_to,
			amount=row.amount,
			at=row.at,
			category=None,
			import_job=import_job,
			sourcink_from=sourcink_unknown,
			sourcink_to=sourcink_unknown,
		)
	crud.import_job_finish(db, import_job)

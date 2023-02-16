import asyncio
import codecs
import csv
import datetime
import logging
from pathlib import Path
import tempfile

from budgery.db import crud

LOGGER = logging.getLogger(__name__)

def _import_afcu_transaction(
	account_id: int,
	data,
	db,
	import_job,
	user) -> None:
	"Process a single line of an America First Credit Union CSV."
	date = datetime.date.fromisoformat(data["Date"])
	time = datetime.time(0, 1, 2, 3)
	at = datetime.datetime.combine(date, time)
	description = data["Description"]
	if "Pending -" in description:
		return
	sourcink_unknown = crud.sourcink_get_or_create(db, "Unknown")
	if data["Debit"]:
		amount = float(data["Debit"])
		account_id_from = account_id
		account_id_to = sourcink_unknown
	elif data["Credit"]:
		amount = float(data["Credit"])
		account_id_to = account_id
		account_id_from = sourcink_unknown
	else:
		raise Exception("No value for debit or credit.")
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
	
def _import_ally_transaction(
	account_id: int,
	data,
	db,
	import_job,
	user) -> None:
	"Process a single line of an Ally Bank CSV."
	date = datetime.date.fromisoformat(data["Date"])
	time = datetime.time.fromisoformat(data["Time"])
	at = datetime.datetime.combine(date, time)
	amount = float(data["Amount"])
	description = data["Description"]
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

def _import_everydollar_transaction(account_id: int, data, db, import_job, user) -> None:
	"Process a single line of an Every Dollar CSV."
	at = datetime.datetime.fromisoformat(data["date"])
	amount = float(data["amount"])
	category = data["description"]
	sourcink_name_from = data["source_name"]
	sourcink_name_to = data["destination_name"]
	sourcink_from = crud.sourcink_get_or_create(db, sourcink_name_from)
	sourcink_to = crud.sourcink_get_or_create(db, sourcink_name_to)
	crud.transaction_create(
		db=db,
		amount=amount,
		at=at,
		category=category,
		import_job=import_job,
		sourcink_from=sourcink_from,
		sourcink_to=sourcink_to,
	)


HEADER_TO_PROCESSOR = {(
	"user_id",
	"group_id",
	"journal_id",
	"created_at",
	"updated_at",
	"group_title",
	"type",
	"amount",
	"foreign_amount",
	"currency_code",
	"foreign_currency_code",
	"description",
	"date",
	"source_name",
	"source_iban",
	"source_type",
	"destination_name",
	"destination_iban",
	"destination_type",
	"reconciled",
	"category",
	"budget",
	"bill",
	"tags",
	"notes",
	"sepa_cc",
	"sepa_ct_op",
	"sepa_ct_id",
	"sepa_db",
	"sepa_country",
	"sepa_ep",
	"sepa_ci",
	"sepa_batch_id",
	"external_uri",
	"interest_date",
	"book_date",
	"process_date",
	"due_date",
	"payment_date",
	"invoice_date",
	"recurrence_id",
	"internal_reference",
	"bunq_payment_id",
	"import_hash",
	"import_hash_v2",
	"external_id",
	"original_source",
	"recurrence_total",
	"recurrence_count",
): _import_everydollar_transaction, (
	"Date",
	" Time",
	" Amount",
	" Type",
	" Description",
): _import_ally_transaction, (
	"Date",
	"No.",
	"Description",
	"Debit",
	"Credit",
): _import_afcu_transaction,
}

def _csv_iterator(f: tempfile.TemporaryFile):
	reader = csv.reader(codecs.iterdecode(f, "UTF-8"), delimiter=",", quotechar="\"")
	header = tuple(next(reader))
	return header, reader

def _processor_from_header(header):
	"Get the processor based on the header"
	for header_pattern, p in HEADER_TO_PROCESSOR.items():
		if header == header_pattern:
			return p
	if not processor:
		raise Exception(f"No header pattern found that matches {header}")

def _clean_data_iterator(header, reader):
	for row in reader:
		yield {header[i].strip(): row[i] for i in range(len(header))}

async def process_transaction_upload(
		csv_file: tempfile.TemporaryFile,
		db,
		import_job,
		user,
	) -> None:
	await asyncio.sleep(0)
	header, reader = _csv_iterator(csv)
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

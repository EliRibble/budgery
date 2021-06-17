import asyncio
import codecs
import csv
import datetime
import logging

from budgery.db import crud

LOGGER = logging.getLogger(__name__)
HEADER = [
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
]

async def process_transaction_upload(
		csv_file,
		db,
		import_job,
		user,
	) -> None:
	await asyncio.sleep(0)
	reader = csv.reader(codecs.iterdecode(csv_file.file, "UTF-8"), delimiter=",", quotechar="\"")
	header = None
	for n, row in enumerate(reader):
		if not header:
			header = row
			for i, val in enumerate(HEADER):
				if not row[i] == val:
					raise ValueError(
						"Header is not what we expected at column {} ({})".format(
							i, val))
			continue
		data = {header[i]: row[i] for i in range(len(header))}
		_import_transaction(
			data=data,
			db=db,
			import_job=import_job,
			user=user,
		)
		LOGGER.info("Handled row %d", n)
	crud.import_job_finish(db, import_job)
	
def _import_transaction(data, db, import_job, user) -> None:
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

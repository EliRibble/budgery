import codecs
import csv
import datetime
import io
import logging
from typing import Iterable, List, Mapping, Optional, Tuple

from budgery.dataclasses import ImportRow

LOGGER = logging.getLogger(__name__)

# Fake type definitions for CSV classes which are implemented in C and
# the classes are *not* exposed anywhere.
# class CSVReader(Generic):
	# @abstractmethod __iter__(self) -> 
def _process_afcu_transaction(data: Mapping[str, str]) -> Optional[ImportRow]:
	"Process a single line of an America First Credit Union CSV."
	at = datetime.datetime.strptime(data["Date"], "%m/%d/%Y")
	description = data["Description"]
	if "Pending -" in description:
		return
	if data["Debit"]:
		amount = float(data["Debit"])
		account_id_is_from = True
	elif data["Credit"]:
		amount = float(data["Credit"])
		account_id_is_from = False
	else:
		raise Exception("No value for debit or credit.")
	return ImportRow(
		account_id_is_from=account_id_is_from,
		amount=amount,
		at=at,
		category=None,
		description=description,
		sourcink_from=None,
		sourcink_to=None,
	)
	
def _process_ally_transaction(data: Mapping[str, str]) -> Optional[ImportRow]:
	"Process a single line of an Ally Bank CSV."
	date = datetime.date.fromisoformat(data["Date"])
	time = datetime.time.fromisoformat(data["Time"])
	at = datetime.datetime.combine(date, time)
	amount = float(data["Amount"])
	description = data["Description"]
	type_ = data["Type"]
	if type_ == "Withdrawal":
		account_id_is_from = True
	elif type_ == "Deposit":
		account_id_is_from = False
	else:
		raise Exception(f"Unknown type {type_}")

	return ImportRow(
		account_id_is_from=account_id_is_from,
		amount=amount,
		at=at,
		category=None,
		description=description,
		sourcink_from=None,
		sourcink_to=None,
	)
	

def _process_everydollar_transaction(data: Mapping[str, str]) -> Optional[ImportRow]:
	"Process a single line of an Every Dollar CSV."
	at = datetime.datetime.fromisoformat(data["date"])
	amount = float(data["amount"])
	category = data["description"]
	sourcink_name_from = data["source_name"]
	sourcink_name_to = data["destination_name"]
	return ImportRow(
		account_id_is_from=True,
		amount=amount,
		at=at,
		category=category,
		description=None,
		sourcink_from=sourcink_name_from,
		sourcink_to=sourcink_name_to,
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
): _process_everydollar_transaction, (
	"Date",
	"Time",
	"Amount",
	"Type",
	"Description",
): _process_ally_transaction, (
	"Date",
	"No.",
	"Description",
	"Debit",
	"Credit",
): _process_afcu_transaction
}

def _processor_from_header(header):
	"Get the processor based on the header"
	for header_pattern, p in HEADER_TO_PROCESSOR.items():
		if header == header_pattern:
			return p
	raise Exception(f"No header pattern found that matches {header}")

def extract_rows(content: bytes) -> List[ImportRow]:
	decoded = codecs.decode(content, "UTF-8")
	dialect = csv.Sniffer().sniff(decoded)
	reader = csv.DictReader(io.StringIO(decoded), dialect=dialect)
	# Fix bad files where the fields end up with whitespace, like Ally
	reader.fieldnames = [f.strip() for f in reader.fieldnames]
	processor = _processor_from_header(tuple(reader.fieldnames))
	rows = [processor(line) for line in reader]
	# Remove empty rows caused by the processor dropping a row
	rows = [r for r in rows if r]
	return rows

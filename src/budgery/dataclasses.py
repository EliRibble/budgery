import dataclasses
import datetime
from typing import Optional

@dataclasses.dataclass
class ImportRow:
	"""A single row of an import with the ideal data.

	The different fields will be populated in different ways depending on
	the data available from a particular source.
	"""
	# True if the account ID should be treated as the account the transaction debits from.
	# False if the account ID should be treated as the account the transaction deposits to.
	account_id_is_from: bool
	amount: float
	at: datetime.datetime
	category: Optional[str]
	description: str
	sourcink_from: Optional[str]
	sourcink_to: Optional[str]
	

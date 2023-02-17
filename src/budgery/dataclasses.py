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
	# Amount in local currency of the transaction
	amount: float
	# Date and time (if available)
	at: datetime.datetime
	# Description from the provider
	description: str
	# Name of the sourcink the amount of money came from
	sourcink_from: Optional[str]
	# Name of the sourcink the amount of money went to
	sourcink_to: Optional[str]
	# Address where the transaction occurred
	address: Optional[str] = None
	# Category from the provider
	category: Optional[str] = None
	# City where the transaction occurred
	city: Optional[str] = None
	# Country where the transaction occurred
	country: Optional[str] = None
	# Any extended details from the provider
	extended_details: Optional[str] = None
	# Reference ID from the provider's internal systems
	reference: Optional[str] = None
	# ZIP code where the transaction occurred
	zipcode: Optional[str] = None
	

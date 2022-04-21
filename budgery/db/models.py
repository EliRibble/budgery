import datetime
import enum
from typing import Optional

from sqlalchemy import Boolean, Column, Date, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship

from budgery.db.history_meta import Versioned

Base = declarative_base()

class Account(Versioned, Base):
	__tablename__ = "account"

	id = Column(Integer, primary_key=True, index=True)
	created = Column(DateTime, default=datetime.datetime.now)
	institution_id = Column(Integer, ForeignKey("institution.id"))
	name = Column(String)

	def __eq__(self, other) -> bool:
		if other is None:
			return False
		if not isinstance(other, Account):
			raise ValueError("Not the same type, can't compare")
		return other.id == self.id


class AccountPermissionType(enum.Enum):
	owner = 1

class AccountPermission(Base):
	__tablename__ = "account_permission"
	account_id = Column(Integer, ForeignKey("account.id"), primary_key=True)
	user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
	type = Column(Enum(AccountPermissionType))

	def __init__(self, account: "Account", type: AccountPermissionType, user: "User") -> None:
		self.account = account
		self.type = type
		self.user = user

class Budget(Versioned, Base):
	__tablename__ = "budget"
	id = Column(Integer, primary_key=True, index=True)
	start_date = Column(Date)
	end_date = Column(Date)

	def __eq__(self, other) -> bool:
		if other is None:
			return False
		if not isinstance(other, Budget):
			raise ValueError("Not the same type, can't compare")
		return other.id == self.id

class BudgetPermissionType(enum.Enum):
	owner = 1

class BudgetPermission(Base):
	__tablename__ = "budget_permission"
	budget_id = Column(Integer, ForeignKey("budget.id"), primary_key=True)
	user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
	type = Column(Enum(BudgetPermissionType))

	def __init__(self, budget: "Budget", type: BudgetPermissionType, user: "User") -> None:
		self.budget = budget
		self.type = type
		self.user = user

class BudgetEntry(Base):
	__tablename__ = "budget_entry"
	id = Column(Integer, primary_key=True, index=True)
	budget_id = Column(Integer, ForeignKey("budget.id"))
	amount = Column(Float)
	category = Column(String, nullable=True)
	name = Column(String)

	def __init__(self, amount: int, budget: "Budget", category: Optional[str], name: str) -> None:
		self.amount = amount
		self.budget_id = budget.id
		self.category = category
		self.name = name

class ImportJobStatus(enum.Enum):
	error = 0
	started = 1
	finished = 2

class ImportJob(Base):
	"A background task to import a large set of transactions."
	__tablename__ = "import_job"
	id = Column(Integer, primary_key=True, index=True)
	account_id = Column(Integer, ForeignKey("account.id"), nullable=True)
	created = Column(DateTime, default=datetime.datetime.now)
	filename = Column(String)
	status = Column(Enum(ImportJobStatus))
	user_id = Column(Integer, ForeignKey("user.id"))

	def __init__(self, filename: str, status: ImportJobStatus, user: "User") -> None:
		self.filename = filename
		self.status = status
		self.user = user

class Institution(Base):
	__tablename__ = "institution"
	id = Column(Integer, primary_key=True, index=True)
	name = Column(String)
	aba_routing_number = Column(Integer)

class LogEntry(Base):
	"A log entry."
	__tablename__ = "logentry"
	id = Column(Integer, primary_key=True, index=True)
	at = Column(DateTime())
	content = Column(String)
	user_id = Column(Integer, ForeignKey("user.id"))

class Sourcink(Base):
	"""A source or sink for transactions.

	Sourcinks are shared between all users in the system.
	"""
	__tablename__ = "sourcink"
	id = Column(Integer, primary_key=True, index=True)
	account_id = Column(Integer, ForeignKey("account.id", name="fk_account_id"), nullable=True)
	name = Column(String())

	def __init__(self, account: Optional["Account"], name: str) -> None:
		self.account = account
		self.name = name
	
class Transaction(Base):
	"""A transaction in the real world that moved money to/from a real world account.

	The transaction should always include at least one account to/from and may include
	up to one sourcink to/from. It is invalid to have both sourcink from and to
	populated."""
	__tablename__ = "transaction"

	id = Column(Integer, primary_key=True, index=True)
	amount = Column(Float)
	at = Column(DateTime())
	budget_entry = Column(Integer, ForeignKey("budget_entry.id", name="fk_budget_entry_id"), nullable=True)
	category = Column(String(), nullable=True)
	import_job_id = Column(Integer, ForeignKey("import_job.id", name="fk_import_job_id"), nullable=True)
	sourcink_id_from = Column(Integer, ForeignKey("sourcink.id", name="fk_sourcink_id_from"), nullable=True)
	sourcink_id_to = Column(Integer, ForeignKey("sourcink.id", name="fk_sourcink_id_to"), nullable=True)

	def __init__(self,
		amount: float,
		at: datetime.datetime,
		sourcink_from: Sourcink,
		sourcink_to: Sourcink,
		budget_entry: Optional[BudgetEntry] = None,
		category: Optional[str] = None,
		import_job: Optional[ImportJob] = None,
	) -> None:
		self.amount = amount
		self.at = at
		self.budget_entry = budget_entry
		self.category = category
		self.import_job = import_job
		self.sourcink_from = sourcink_from
		self.sourcink_to = sourcink_to
		

class User(Base):
	__tablename__ = "user"

	id = Column(Integer, primary_key=True, index=True)
	email = Column(String)
	username = Column(String, index=True)


Institution.accounts = relationship(Account, back_populates="institution")
Account.institution = relationship(Institution, back_populates="accounts")
AccountHistory = Account.__history_mapper__.class_
AccountPermission.account = relationship(Account)
AccountPermission.user = relationship(User,
	backref=backref("user_account_permissions", cascade="all, delete-orphan"))
BudgetHistory = Budget.__history_mapper__.class_
BudgetPermission.budget = relationship(Budget)
BudgetPermission.user = relationship(User,
	backref=backref("user_budget_permissions", cascade="all, delete-orphan"))
BudgetEntry.budget = relationship(Budget)
BudgetEntry.transactions = relationship(Transaction)
ImportJob.user = relationship(User)
Sourcink.account = relationship(Account)
Transaction.budget_entry = relationship(BudgetEntry, back_populates="transactions")
Transaction.sourcink_from = relationship(Sourcink, foreign_keys=[Transaction.sourcink_id_from])
Transaction.sourcink_to = relationship(Sourcink, foreign_keys=[Transaction.sourcink_id_to])
User.accounts = association_proxy("user_account_permissions", "account")
User.budgets = association_proxy("user_budget_permissions", "budget")

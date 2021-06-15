import datetime
import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String
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
	name = Column(String())
	
class Transaction(Base):
	"""A transaction in the real world that moved money to/from a real world account.

	The transaction should always include at least one account to/from and may include
	up to one sourcink to/from. It is invalid to have both sourcink from and to
	populated."""
	__tablename__ = "transaction"

	id = Column(Integer, primary_key=True, index=True)
	account_id_from = Column(Integer, ForeignKey("account.id", name="fk_account_id_from"), nullable=True)
	account_id_to = Column(Integer, ForeignKey("account.id", name="fk_account_id_to"), nullable=True)
	amount = Column(Float)
	at = Column(DateTime())
	category = Column(String(), nullable=True)
	sourcink_id_from = Column(Integer, ForeignKey("sourcink.id", name="fk_sourcink_id_from"), nullable=True)
	sourcink_id_to = Column(Integer, ForeignKey("sourcink.id", name="fk_sourcink_id_to"), nullable=True)

class User(Base):
	__tablename__ = "user"

	id = Column(Integer, primary_key=True, index=True)
	email = Column(String)
	username = Column(String, index=True)


Institution.accounts = relationship("Account", back_populates="institution")
Account.institution = relationship("Institution", back_populates="accounts")
AccountHistory = Account.__history_mapper__.class_
AccountPermission.account = relationship("Account")
AccountPermission.user = relationship(User,
	backref=backref("user_account_permissions", cascade="all, delete-orphan"))
User.accounts = association_proxy("user_account_permissions", "account")

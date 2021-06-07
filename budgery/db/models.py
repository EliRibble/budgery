import datetime
import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

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

AccountHistory = Account.__history_mapper__.class_

class AccountPermissionType(enum.Enum):
	owner = 1

class AccountPermission(Base):
	__tablename__ = "account_permission"
	id = Column(Integer, primary_key=True, index=True)
	account_id = Column(Integer, ForeignKey("account.id"))
	type = Column(Enum(AccountPermissionType))
	user_id = Column(Integer, ForeignKey("user.id"))

class Institution(Base):
	__tablename__ = "institution"
	id = Column(Integer, primary_key=True, index=True)
	name = Column(String)
	aba_routing_number = Column(Integer)

	accounts = relationship("Account", back_populates="institution")
Account.institution = relationship("Institution", back_populates="accounts")

class LogEntry(Base):
	"A log entry."
	__tablename__ = "logentry"
	id = Column(Integer, primary_key=True, index=True)
	at = Column(DateTime())
	content = Column(String)
	user_id = Column(Integer, ForeignKey("user.id"))
	
class Transaction(Base):
	__tablename__ = "transaction"

	id = Column(Integer, primary_key=True, index=True)
	amount = Column(Float)

class User(Base):
	__tablename__ = "user"

	id = Column(Integer, primary_key=True, index=True)
	email = Column(String)
	username = Column(String, index=True)

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Account(Base):
	__tablename__ = "account"

	id = Column(Integer, primary_key=True, index=True)
	name = Column(String)
	owner_id = Column(Integer, ForeignKey("user.id"))

	owner = relationship("User", back_populates="accounts")

class Institution(Base):
	__tablename__ = "institution"
	id = Column(Integer, primary_key=True, index=True)
	name = Column(String)
	aba_routing_number = Column(Integer)

class Transaction(Base):
	__tablename__ = "transaction"

	id = Column(Integer, primary_key=True, index=True)
	amount = Column(Float)

class User(Base):
	__tablename__ = "user"

	id = Column(Integer, primary_key=True, index=True)
	email = Column(String)
	username = Column(String, index=True)
	accounts = relationship("Account", back_populates="owner")



from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Transaction(Base):
	__tablename__ = "transaction"

	id = Column(Integer, primary_key=True, index=True)
	amount = Column(Float)

class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True, index=True)
	email = Column(String, unique=True, index=True)
	hashed_password = Column(String)
	is_active = Column(Boolean, default=True)

	items = relationship("Item", back_populates="owner")


class Item(Base):
	__tablename__ = "items"

	id = Column(Integer, primary_key=True, index=True)
	title = Column(String, index=True)
	description = Column(String, index=True)
	owner_id = Column(Integer, ForeignKey("users.id"))

	owner = relationship("User", back_populates="items")

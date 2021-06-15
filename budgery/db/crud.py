import logging
from typing import Iterable

from sqlalchemy.orm import Session

from budgery.db import models
from budgery.db import schemas
from budgery.user import User


LOGGER = logging.getLogger(__name__)

def account_create(db: Session, institution_id: int, name: str, user: models.User) -> models.Account:
	account = models.Account(
		institution_id = institution_id,
		name = name,
	)
	permission = models.AccountPermission(
		account=account,
		type=models.AccountPermissionType.owner,
		user=user,
	)
	user.user_account_permissions.append(permission)
	db.commit()

def account_get_by_id(db: Session, account_id: int) -> models.Account:
	return db.query(models.Account).filter_by(id=account_id).first()

def account_history_list_by_account_id(db: Session, account_id: int) -> Iterable[models.AccountHistory]:
	return db.query(models.AccountHistory).all()

def account_list(db: Session, user: models.User):
	return db.query(models.Account).all()

def account_update(db: Session, account: int, institution: int, name: str) -> None:
	account.name = name
	account.institution = institution
	db.commit()
	
def create_tables(db: Session):
	models.Base.metadata.create_all(bind=db)

def institution_get_by_name(db: Session, name: str) -> models.Institution:
	return db.query(models.Institution).filter(name==name).first()

def institution_list(db: Session):
	return db.query(models.Institution).all()

def institution_create(db: Session, user: User, aba_routing_number: int, name: str) -> models.Institution:
	institution = models.Institution(
		aba_routing_number=aba_routing_number,
		name=name,
	)
	db.add(institution)
	db.commit()
	LOGGER.info("Created %s", institution)
	return institution

def transaction_create(db: Session, amount: int):
	transaction = models.Transaction(amount=amount)
	db.add(transaction)
	db.commit()
	return transaction

def transaction_list(db: Session):
	return db.query(models.Transaction).all()

def get_user_by_email(db: Session, email: str):
	return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
	return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
	fake_hashed_password = user.password + "notreallyhashed"
	db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
	db.add(db_user)
	db.commit()
	db.refresh(db_user)
	return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
	return db.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
	db_item = models.Item(**item.dict(), owner_id=user_id)
	db.add(db_item)
	db.commit()
	db.refresh(db_item)
	return db_item

def user_ensure_exists(db: Session, user: User) -> None:
	existing = user_get_by_username(db, user.username)
	if existing:
		return
	user = models.User(
		email = user.email,
		username = user.username,
	)
	db.add(user)
	db.commit()

def user_get_by_username(db: Session, username: str):
	return db.query(models.User).filter(models.User.username == username).first()

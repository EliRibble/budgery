import datetime
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
	sourcink = models.Sourcink(
		account = account,
		name = name,
	)
	db.add(account)
	db.add(sourcink)
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

def category_list(db: Session) -> Iterable[str]:
	return db.query(models.Transaction.category).all()

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

def sourcink_list(db: Session) -> Iterable[models.Sourcink]:
	return db.query(models.Sourcink).all()

def sourcink_get_or_create(
		db: Session,
		name: str,
	) -> models.Sourcink:
	found = db.query(models.Sourcink).filter_by(name=name).first()
	if found:
		return found
	sourcink = models.Sourcink(
		account=None,
		name=name,
	)
	db.add(sourcink)
	db.commit()
	return sourcink

def transaction_create(
		db: Session,
		amount: float,
		at: datetime.datetime,
		category: str,
		sourcink_from: models.Sourcink,
		sourcink_to: models.Sourcink,
	) -> models.Transaction:
	transaction = models.Transaction(
		amount=amount,
		at=at,
		category=category,
		sourcink_from=sourcink_from,
		sourcink_to=sourcink_to,
	)
	db.add(transaction)
	db.commit()
	return transaction

def transaction_list(db: Session):
	return db.query(models.Transaction).all()

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

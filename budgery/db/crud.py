from sqlalchemy.orm import Session

from budgery.db import models
from budgery.db import schemas
from budgery.user import User


def create_tables(db: Session):
	models.Base.metadata.create_all(bind=db)

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



from typing import List, Optional

from pydantic import BaseModel


class ItemBase(BaseModel):
	title: str
	description: Optional[str] = None


class ItemCreate(ItemBase):
	pass


class Item(ItemBase):
	id: int
	owner_id: int

	model_config = {
		"from_attributes": True
	}


class UserBase(BaseModel):
	email: str


class UserCreate(UserBase):
	password: str


class User(UserBase):
	id: int
	is_active: bool
	items: List[Item] = []

	model_config = {
		"from_attributes": True
	}

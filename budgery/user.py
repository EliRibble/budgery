import datetime
from typing import Optional

from pydantic import BaseModel

class User(BaseModel):
	auth_time: datetime.datetime
	email: Optional[str] = None
	email_verified: bool
	expiration: datetime.datetime
	family_name: Optional[str] = None
	given_name: Optional[str] = None
	name: str
	disabled: Optional[bool] = None
	username: str

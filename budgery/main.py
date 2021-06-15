import datetime
from typing import Mapping, Union

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse

from budgery.db import connection as db_connection
from budgery.db import crud
from budgery.user import User

app = FastAPI()
config = Config("env")
db_engine = db_connection.connect(config)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(SessionMiddleware, secret_key=config("SECRET_KEY"))
oauth = OAuth(config)
templates = Jinja2Templates(directory="templates") 

oauth.register(
	name="keycloak",
	server_metadata_url=config("KEYCLOAK_METADATA_URL"),
	client_kwargs={
		"scope": "openid email profile"
	}
)

def get_db():
	db = db_connection.session(db_engine)
	try:
		yield db
	finally:
		db.close()

def get_user(request: Request) -> User:
	user_data = request.session.get("user")
	return _parse_user(user_data)

def _parse_user(user_data: Mapping[str, Union[int, str]]) -> User:
	user_model = User(
		auth_time = user_data["auth_time"],
		disabled = False,
		email = user_data["email"],
		email_verified = user_data["email_verified"],
		expiration = user_data["exp"],
		family_name = user_data["family_name"],
		given_name = user_data["given_name"],
		name = user_data["name"],
		username = user_data["preferred_username"],)	
	return user_model

@app.get("/", response_class=HTMLResponse)
async def root(request: Request, db: Session = Depends(get_db)):
	user_ = request.session.get("user")
	return templates.TemplateResponse("index.html.jinja", {"request": request, "user": user_})

@app.get("/account")
async def account_list_get(request: Request, db: Session = Depends(get_db), user: User = Depends(get_user)):
	institutions = crud.institution_list(db)
	db_user = crud.user_get_by_username(db, user.username)
	accounts = db_user.accounts
	return templates.TemplateResponse("account-list.html.jinja", {
		"accounts": accounts,
		"current_page": "account",
		"institutions": institutions,
		"request": request,
		"user": user})

@app.get("/account/create")
async def accounts_create_get(request: Request, db: Session = Depends(get_db)):
	user_ = request.session.get("user")
	institutions = crud.institution_list(db)
	return templates.TemplateResponse("account-create.html.jinja", {
		"institutions": institutions,
		"request": request,
		 "user": user_
	})

@app.post("/account/create")
async def accounts_create_post(request: Request, db: Session = Depends(get_db), user: User = Depends(get_user), name: str = Form(...), institution_name: str = Form(...)):
	db_user = crud.user_get_by_username(db, user.username)
	institution = crud.institution_get_by_name(db, institution_name)
	crud.account_create(
		db = db,
		institution_id = institution.id,
		name = name,
		user = db_user,
	)
	return RedirectResponse(status_code=303, url="/account")

@app.get("/account/{account_id}")
async def account_get(request: Request, account_id: int, db: Session = Depends(get_db)):
	user_ = request.session.get("user")
	account = crud.account_get_by_id(db, account_id)
	history = crud.account_history_list_by_account_id(db, account_id)
	return templates.TemplateResponse("account.html.jinja", {
		"account": account,
		"current_page": "account",
		"history": history,
		"request": request,
		"user": user_})

@app.get("/account/{account_id}/edit")
async def account_edit_get(request: Request, account_id: int, db: Session = Depends(get_db)):
	user_ = request.session.get("user")
	account = crud.account_get_by_id(db, account_id)
	return templates.TemplateResponse("account-edit.html.jinja", {
		"account": account,
		"current_page": "account",
		"request": request,
		"user": user_})

@app.post("/account/{account_id}/edit")
async def account_edit_post(request: Request, account_id: int, name: str = Form(...), institution_name: str = Form(...), db: Session = Depends(get_db)):
	user_ = request.session.get("user")
	account = crud.account_get_by_id(db, account_id)
	institution = crud.institution_get_by_name(db, institution_name)
	crud.account_update(db,
		account=account,
		institution=institution,
		name=name,
	)
	return RedirectResponse(status_code=303, url=f"/account/{account.id}")

@app.route("/allocation")
async def allocation(request: Request):
	user_ = request.session.get("user")
	return templates.TemplateResponse("allocation.html.jinja", {
		"current_page": "allocation",
		"request": request,
		"user": user_})

@app.get("/auth", response_class=HTMLResponse)
async def auth(request: Request, db: Session = Depends(get_db)):
	try:
		token = await oauth.keycloak.authorize_access_token(request)
	except OAuthError as error:
		return HTMLResponse(f"<h1>{error.error}</h1>")
	user_ = await oauth.keycloak.parse_id_token(request, token)
	user_model = _parse_user(user_)
	crud.user_ensure_exists(db, user_model)
	request.session["user"] = dict(user_)
	return RedirectResponse(url="/")

@app.get("/category")
async def category(request: Request):
	user_ = request.session.get("user")
	return templates.TemplateResponse("category.html.jinja", {
		"current_page": "category",
		"request": request,
		"user": user_})

@app.route("/login")
async def login(request: Request):
	redirect_uri = request.url_for("auth")
	return await oauth.keycloak.authorize_redirect(request, redirect_uri)

@app.route("/logout")
async def logout(request: Request):
	request.session.pop("user", None)
	return RedirectResponse(url="/")

@app.get("/institution")
async def institution_get(request: Request, db: Session = Depends(get_db)):
	user_ = request.session.get("user")
	institutions = crud.institution_list(db)
	return templates.TemplateResponse("institution-list.html.jinja", {
		"current_page": "institution",
		"institutions": institutions,
		"request": request,
		"user": user_})

@app.get("/institution/create")
async def institution_create_get(request: Request):
	user_ = request.session.get("user")
	return templates.TemplateResponse("institution-create.html.jinja", {
		"current_page": "institution",
		"request": request,
		"user": user_})

@app.post("/institution/create")
async def institution_create_post(request: Request, db: Session = Depends(get_db), aba_routing_number: int = Form(...), name: str = Form(...)):
	user_ = request.session.get("user")
	crud.institution_create(
		aba_routing_number=aba_routing_number,
		db=db,
		name=name,
		user=user_,
	)
	return RedirectResponse(status_code=303, url="/institution")

@app.get("/report")
async def report(request: Request):
	user_ = request.session.get("user")
	return templates.TemplateResponse("report.html.jinja", {
		"current_page": "report",
		"request": request,
		"user": user_})

@app.get("/tag")
async def tag(request: Request):
	user_ = request.session.get("user")
	return templates.TemplateResponse("tag.html.jinja", {
		"current_page": "tag",
		"request": request,
		"user": user_})

@app.get("/transaction", response_class=HTMLResponse)
async def transaction_list_get(request: Request, db: Session = Depends(get_db)):
	user_ = request.session.get("user")
	transactions = crud.transaction_list(db)
	return templates.TemplateResponse("transaction-list.html.jinja", {
		"current_page": "transaction",
		"request": request,
		"transactions": transactions,
		"user": user_})

@app.post("/transaction")
async def transaction_list_post(request: Request, amount: float, db: Session = Depends(get_db)):
	crud.transaction_create(db, amount)
	return RedirectResponse(url="/transactions")

@app.get("/transaction/create")
async def transaction_create_get(request: Request, db: Session = Depends(get_db), user: User = Depends(get_user)):
	db_user = crud.user_get_by_username(db, user.username)
	categories = crud.category_list(db)
	sourcinks = crud.sourcink_list(db)
	return templates.TemplateResponse("transaction-create.html.jinja", {
		"categories": categories,
		"request": request,
		"sourcinks": sourcinks,
		"user": user,
	})

@app.post("/transaction/create")
async def transaction_create_post(
	request: Request,
	db: Session = Depends(get_db),
	user: User = Depends(get_user),
	sourcink_name_from: str = Form(...),
	sourcink_name_to: str = Form(...),
	amount: float = Form(...),
	at: str = Form(...)):
	at_date = datetime.date.fromisoformat(at)
	at_datetime = datetime.datetime(
		year=at_date.year,
		month=at_date.month,
		day=at_date.day,
	)
	db_user = crud.user_get_by_username(db, user.username)
	sourcink_from = crud.sourcink_get_or_create(db, sourcink_name_from)
	sourcink_to = crud.sourcink_get_or_create(db, sourcink_name_to)
	crud.transaction_create(
		amount=amount,
		at=at_datetime,
		category=category,
		db=db,
		sourcink_from=sourcink_from,
		sourcink_to=sourcink_to,
	)
	return RedirectResponse(url="/transaction")

@app.get("/user")
async def user_get(request: Request, db: Session = Depends(get_db), user: User = Depends(get_user)):
	user_data = request.session.get("user")
	db_user = crud.user_get_by_username(db, user.username)
	return templates.TemplateResponse("user.html.jinja", {
		"current_page": "user",
		"db_user": db_user,
		"request": request,
		"user": user,
		"user_data": user_data,})

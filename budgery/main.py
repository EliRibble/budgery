import calendar
import datetime
from typing import Mapping, Optional, Union

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import BackgroundTasks, Depends, FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse

from budgery import custom_filters, dates, task
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
templates.env.filters["currency"] = custom_filters.currency

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

def get_user(request: Request) -> Optional[User]:
	user_data = request.session.get("user")
	if user_data is None:
		return None
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
async def root(request: Request, db: Session = Depends(get_db), user: User = Depends(get_user)):
	return templates.TemplateResponse("index.html.jinja", {"request": request, "user": user})

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
async def accounts_create_get(request: Request, db: Session = Depends(get_db), user: User = Depends(get_user)):
	institutions = crud.institution_list(db)
	return templates.TemplateResponse("account-create.html.jinja", {
		"institutions": institutions,
		"request": request,
		 "user": user
	})

@app.post("/account/create")
async def accounts_create_post(
		request: Request,
		db: Session = Depends(get_db),
		user: User = Depends(get_user),
		name: str = Form(...),
		institution_name: str = Form(...)):
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
async def account_get(request: Request,
	account_id: int,
	db: Session = Depends(get_db),
	user: User = Depends(get_user)):
	account = crud.account_get_by_id(db, account_id)
	history = crud.account_history_list_by_account_id(db, account_id)
	return templates.TemplateResponse("account.html.jinja", {
		"account": account,
		"current_page": "account",
		"history": history,
		"request": request,
		"user": user})

@app.get("/account/{account_id}/edit")
async def account_edit_get(request: Request, account_id: int, db: Session = Depends(get_db), user: User = Depends(get_user)):
	account = crud.account_get_by_id(db, account_id)
	return templates.TemplateResponse("account-edit.html.jinja", {
		"account": account,
		"current_page": "account",
		"request": request,
		"user": user_})

@app.post("/account/{account_id}/edit")
async def account_edit_post(
		request: Request,
		account_id: int,
		name: str = Form(...),
		institution_name: str = Form(...),
		db: Session = Depends(get_db)):
	account = crud.account_get_by_id(db, account_id)
	institution = crud.institution_get_by_name(db, institution_name)
	crud.account_update(db,
		account=account,
		institution=institution,
		name=name,
	)
	return RedirectResponse(status_code=303, url=f"/account/{account.id}")

@app.route("/allocation")
async def allocation(request: Request, user: User = Depends(get_user)):
	return templates.TemplateResponse("allocation-list.html.jinja", {
		"current_page": "allocation",
		"request": request,
		"user": user})

@app.get("/auth", response_class=HTMLResponse)
async def auth(request: Request, db: Session = Depends(get_db)):
	try:
		token = await oauth.keycloak.authorize_access_token(request)
	except OAuthError as error:
		return HTMLResponse(f"<h1>{error.error}</h1>")
	user = await oauth.keycloak.parse_id_token(request, token)
	user_model = _parse_user(user)
	crud.user_ensure_exists(db, user_model)
	request.session["user"] = dict(user)
	return RedirectResponse(url="/")

@app.get("/budget", response_class=HTMLResponse)
async def budget_list_get(
		request: Request,
		db: Session = Depends(get_db),
		user: User = Depends(get_user)):
	db_user = crud.user_get_by_username(db, user.username)
	budgets = db_user.budgets
	return templates.TemplateResponse("budget-list.html.jinja", {
		"budgets": budgets,
		"current_page": "budget",
		"request": request,
		"user": user})

@app.get("/budget/create", response_class=HTMLResponse)
async def budget_create_get(
		request: Request,
		db: Session = Depends(get_db),
		user: User = Depends(get_user)):
	default_end_date = dates.this_month_end()
	default_start_date = dates.this_month_start()
	return templates.TemplateResponse("budget-create.html.jinja", {
		"default_end_date": default_end_date,
		"default_start_date": default_start_date,
		"request": request,
		 "user": user})

@app.post("/budget/create")
async def budget_create_post(
		request: Request,
		db: Session = Depends(get_db),
		user: User = Depends(get_user),
		end_date_str: str = Form(...),
		start_date_str: str = Form(...)):
	db_user = crud.user_get_by_username(db, user.username)
	end_date = datetime.date.fromisoformat(end_date_str)
	start_date = datetime.date.fromisoformat(start_date_str)
	crud.budget_create(
		db = db,
		end_date = end_date,
		start_date = start_date,
		user = db_user)
	return RedirectResponse(status_code=303, url="/budget")
	
@app.get("/budget/{budget_id}/entry/create", response_class=HTMLResponse)
async def budget_entry_create_get(
		request: Request,
		budget_id: int,
		db: Session = Depends(get_db),
		user: User = Depends(get_user)):
	budget = crud.budget_get_by_id(db, budget_id)
	return templates.TemplateResponse("budget-entry-create.html.jinja", {
		"budget": budget,
		"request": request,
		 "user": user})

@app.post("/budget/{budget_id}/entry/create")
async def budget_entry_create_post(
		request: Request,
		budget_id: int,
		db: Session = Depends(get_db),
		user: User = Depends(get_user),
		amount: float = Form(...),
		category: str = Form(...),
		entry_type: str = Form(...),
		name: str = Form(...),
	):
	db_user = crud.user_get_by_username(db, user.username)
	budget = crud.budget_get_by_id(db, budget_id)
	if not budget:
		raise ValueError("No budget with ID %d", budget_id)
	if amount < 0:
		raise ValueError(f"Don't supply negative values like '{amount}', use 'entry_type' instead.")
	if entry_type == "expense":
		amount = amount * -1
	elif entry_type != "income":
		raise ValueError(f"entry_type must be either 'expense' or 'income'. You gave '{entry_type}'")
	crud.budget_entry_create(
		db = db,
		amount = amount,
		budget = budget,
		category = category,
		name = name,
		user = db_user)
	return RedirectResponse(status_code=303, url=f"/budget/{budget_id}")
	
@app.get("/budget/{budget_id}")
async def budget_get(
		request: Request,
		budget_id: int,
		db: Session = Depends(get_db),
		user: User = Depends(get_user)):
	db_user = crud.user_get_by_username(db, user.username)
	budget = crud.budget_get_by_id(db, budget_id)
	entries = crud.budget_entry_list_by_budget(db, budget)
	history = crud.budget_history_list_by_budget_id(db, budget_id)
	net = sum(entry.amount for entry in entries)
	return templates.TemplateResponse("budget.html.jinja", {
		"budget": budget,
		"current_page": "budget",
		"entries": entries,
		"history": history,
		"net": net,
		"request": request,
		"user": user})

@app.get("/category")
async def category_list_get(
		request: Request,
		db: Session = Depends(get_db),
		user: User = Depends(get_user)):
	user = request.session.get("user")
	categories = crud.category_list(db, user)
	return templates.TemplateResponse("category.html.jinja", {
		"categories": categories,
		"current_page": "category",
		"request": request,
		"user": user})

@app.route("/login")
async def login(request: Request):
	redirect_uri = request.url_for("auth")
	return await oauth.keycloak.authorize_redirect(request, redirect_uri)

@app.route("/logout")
async def logout(request: Request):
	request.session.pop("user", None)
	return RedirectResponse(url="/")

@app.get("/import")
async def import_get(request: Request, db: Session = Depends(get_db), user: User = Depends(get_user)):
	db_user = crud.user_get_by_username(db, user.username)
	imports = crud.import_job_list(
		db = db,
		user = db_user,
	)
	return templates.TemplateResponse("import-list.html.jinja", {
		"imports": imports,
		"request": request,
		"user": user,
	})

@app.get("/import/create")
async def import_create_get(request: Request,
	db: Session = Depends(get_db),
	user: User = Depends(get_user)):
	db_user = crud.user_get_by_username(db, user.username)
	accounts = crud.account_list(db, db_user)
	institutions = crud.institution_list(db)
	institutions_by_id = {institution.id: institution for institution in institutions}
	return templates.TemplateResponse("import-create.html.jinja", {
		"accounts": accounts,
		"institutions_by_id": institutions_by_id,
		"request": request,
		"user": user,
	})

@app.post("/import/create")
async def import_create_post(
		request: Request,
		background_tasks: BackgroundTasks,
		account_id: int = Form(...),
		db: Session = Depends(get_db),
		user: User = Depends(get_user),
		csv_file: UploadFile = File(...),
	):
	db_user = crud.user_get_by_username(db, user.username)
	import_job = crud.import_job_create(
		account_id = account_id,
		db = db,
		filename = csv_file.filename,
		user = db_user,
	)
	background_tasks.add_task(
		task.process_transaction_upload,
		csv_file=csv_file,
		db=db,
		import_job=import_job,
		user=db_user,
	)
	return templates.TemplateResponse("import-create.html.jinja", {
		"request": request,
		"user": user,
	})

@app.get("/institution")
async def institution_get(
		request: Request,
		db: Session = Depends(get_db),
		user: User = Depends(get_user)):
	institutions = crud.institution_list(db)
	return templates.TemplateResponse("institution-list.html.jinja", {
		"current_page": "institution",
		"institutions": institutions,
		"request": request,
		"user": user})

@app.get("/institution/create")
async def institution_create_get(request: Request, user: User = Depends(get_user)):
	return templates.TemplateResponse("institution-create.html.jinja", {
		"current_page": "institution",
		"request": request,
		"user": user})

@app.post("/institution/create")
async def institution_create_post(
		request: Request,
		db: Session = Depends(get_db),
		aba_routing_number: int = Form(...),
		name: str = Form(...),
		user: User = Depends(get_user)):
	crud.institution_create(
		aba_routing_number=aba_routing_number,
		db=db,
		name=name,
		user=user,
	)
	return RedirectResponse(status_code=303, url="/institution")

@app.get("/report")
async def report(request: Request, user: User = Depends(get_user)):
	return templates.TemplateResponse("report.html.jinja", {
		"current_page": "report",
		"request": request,
		"user": user})

@app.get("/sourcink", response_class=HTMLResponse)
async def sourcinks_list_get(
		request: Request,
		db: Session = Depends(get_db),
		user: User = Depends(get_user),
		name: str = ""):
	"Get list of sourcinks."
	db_user = crud.user_get_by_username(db, user.username)
	sourcinks = crud.sourcink_list(db, db_user, name=name)
	sourcinks = sorted(sourcinks, key=lambda s: s.name)
	return templates.TemplateResponse("sourcink-list.html.jinja", {
		"request": request,
		"sourcinks": sourcinks,
		"user": user,
	})
	
@app.get("/sourcink/{sourcink_id}", response_class=HTMLResponse)
async def sourcinks_get(
		request: Request,
		sourcink_id: int,
		db: Session = Depends(get_db),
		user: User = Depends(get_user),
		name: str = ""):
	"Get a specific sourcink."
	db_user = crud.user_get_by_username(db, user.username)
	sourcink = crud.sourcink_get_by_id(db, db_user, sourcink_id)
	return templates.TemplateResponse("sourcink.html.jinja", {
		"current_page": "sourcink",
		"request": request,
		"sourcink": sourcink,
		"user": user,
	})
	
@app.get("/tag")
async def tag(request: Request, user: User = Depends(get_user)):
	return templates.TemplateResponse("tag.html.jinja", {
		"current_page": "tag",
		"request": request,
		"user": user})

@app.get("/transaction", response_class=HTMLResponse)
async def transaction_list_get(
		request: Request,
		at_end: Optional[str] = None,
		at_start: Optional[str] = None,
		category: Optional[str] = None,
		db: Session = Depends(get_db),
		user: User = Depends(get_user)):

	at = crud.DatetimeRange(
		end=dates.parse(at_end) if at_end else None,
		start=dates.parse(at_start) if at_start else dates.this_month_start(),
	)
	transactions = crud.transaction_list(
		at=at,
		category=category,
		db=db,
	)
	return templates.TemplateResponse("transaction-list.html.jinja", {
		"at": at,
		"category": category,
		"current_page": "transaction",
		"request": request,
		"transactions": transactions,
		"user": user})

@app.get("/transaction/create")
async def transaction_create_get(
		request: Request,
		db: Session = Depends(get_db),
		user: User = Depends(get_user)):
	db_user = crud.user_get_by_username(db, user.username)
	categories = crud.category_list(db, db_user)
	sourcinks = crud.sourcink_list(db, db_user)
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
	category: str = Form(...),
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
	return RedirectResponse(status_code=303, url="/transaction")

@app.get("/transaction/{transaction_id}")
async def transaction_get(
		request: Request,
		transaction_id: int,
		db: Session = Depends(get_db),
		user: User = Depends(get_user)):
	transaction = crud.transaction_get_by_id(db, transaction_id)
	return templates.TemplateResponse("transaction.html.jinja", {
		"current_page": "account",
		"request": request,
		"transaction": transaction,
		"user": user})

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

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse

from budgery import user
from budgery.db import connection as db_connection
from budgery.db import crud

app = FastAPI()
config = Config("env")
db_engine = db_connection.connect(config)
crud.create_tables(db_engine)

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

@app.get("/", response_class=HTMLResponse)
async def root(request: Request, db: Session = Depends(get_db)):
	user_ = request.session.get("user")
	return templates.TemplateResponse("index.html.jinja", {"request": request, "user": user_})

@app.route("/account")
async def accounts(request: Request):
	user_ = request.session.get("user")
	return templates.TemplateResponse("account.html.jinja", {
		"current_page": "account",
		"request": request,
		"user": user_})

@app.route("/allocation")
async def allocation(request: Request):
	user_ = request.session.get("user")
	return templates.TemplateResponse("allocation.html.jinja", {
		"current_page": "allocation",
		"request": request,
		"user": user_})

@app.get("/accounts/create")
async def accounts_create_get(request: Request):
	user_ = request.session.get("user")
	return templates.TemplateResponse("accounts-create.html.jinja", {"request": request, "user": user_})

@app.post("/accounts/create")
async def accounts_create_post(request: Request, name: str = Form(...)):
	user_ = request.session.get("user")
	return templates.TemplateResponse("accounts-create.html.jinja", {"request": request, "user": user_})

@app.route("/auth")
async def auth(request: Request):
	try:
		token = await oauth.keycloak.authorize_access_token(request)
	except OAuthError as error:
		return HTMLResponse(f"<h1>{error.error}</h1>")
	user = await oauth.keycloak.parse_id_token(request, token)
	request.session["user"] = dict(user)
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
async def institution(request: Request):
	user_ = request.session.get("user")
	return templates.TemplateResponse("institution.html.jinja", {
		"current_page": "institution",
		"request": request,
		"user": user_})

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

@app.post("/transaction")
async def transaction_post(request: Request, amount: float, db: Session = Depends(get_db)):
	crud.transaction_create(db, amount)
	return RedirectResponse(url="/transactions")

@app.get("/transaction", response_class=HTMLResponse)
async def transaction_get(request: Request, db: Session = Depends(get_db)):
	user_ = request.session.get("user")
	transactions = crud.transaction_list(db)
	return templates.TemplateResponse("transactions.html.jinja", {
		"current_page": "transaction",
		"request": request,
		"transactions": transactions,
		"user": user_})

@app.route("/user")
async def user(request: Request):
	user_ = request.session.get("user")
	return templates.TemplateResponse("user.html.jinja", {
		"current_page": "user",
		"request": request,
		"user": user_})

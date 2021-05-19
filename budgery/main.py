from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse

from budgery import user

app = FastAPI()
config = Config("env")
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
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
	user_ = request.session.get("user")
	import pprint
	pprint.pprint(user_)
	return templates.TemplateResponse("index.html.jinja", {"request": request, "user": user_})

@app.route("/login")
async def login(request: Request):
	redirect_uri = request.url_for("auth")
	return await oauth.keycloak.authorize_redirect(request, redirect_uri)

@app.route("/auth")
async def auth(request: Request):
	try:
		token = await oauth.keycloak.authorize_access_token(request)
	except OAuthError as error:
		return HTMLResponse(f"<h1>{error.error}</h1>")
	user = await oauth.keycloak.parse_id_token(request, token)
	request.session["user"] = dict(user)
	return RedirectResponse(url="/")

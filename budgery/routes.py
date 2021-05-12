from quart import Blueprint, render_template

blueprint = Blueprint("all", __name__)

@blueprint.route("/")
async def hello() -> None:
	return await render_template("index.html")


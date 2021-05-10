from quart import Quart, render_template

app = Quart("budgery")

@app.route("/")
async def hello() -> None:
	return await render_template("index.html")

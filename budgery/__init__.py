from quart import Quart

app = Quart("budgery")

@app.route("/")
async def hello() -> None:
	return "Hello World"

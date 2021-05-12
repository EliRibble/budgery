import os
from quart import Quart

import budgery.config
import budgery.routes

def create_app(mode="Development") -> Quart:
	"Create the quart app."
	app = Quart("budgery")
	app.config.from_object(f"budgery.config.{mode}")
	if os.environ.get("BUDGERY_SETTINGS"):
		app.config.from_envvar('BUDGERY_SETTINGS')
	app.register_blueprint(
		budgery.routes.blueprint
	)
	return app

if __name__ == "__main__":
	app = create_app()
	app.run(port=10100)

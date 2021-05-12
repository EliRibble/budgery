import logging
import os
from quart import Quart
import sys

import budgery.config
import budgery.middleware
import budgery.routes

def create_app() -> Quart:
	"Create the quart app."
	config = budgery.config.load()
	app = Quart("budgery")
	app.config.from_mapping(config)
		
	app.register_blueprint(
		budgery.routes.blueprint
	)
	app.asgi_app = budgery.middleware.ReverseProxied(app.asgi_app)
	return app

def main() -> None:
	logging.basicConfig(level=logging.DEBUG)
	try:
		app = create_app()
	except budgery.config.ConfigurationError as ex:
		print(ex)
		sys.exit(1)
	app.run(port=10100)

if __name__ == "__main__":
	main()

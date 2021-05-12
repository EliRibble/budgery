class ReverseProxied:
	def __init__(self, app) -> None:
		self.app = app

	async def __call__(self, scope, receive, send) -> None:
		for header, value in scope.get("headers", {}):
			if header.decode("utf-8") != "x-forwarded-proto":
				continue
			scope["scheme"] = value.decode("utf-8")
		await self.app(scope, receive, send)

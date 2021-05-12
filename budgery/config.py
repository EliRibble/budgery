import os
import toml
from typing import Dict, Union

import requests

DEFAULT_CONFIG_FILE = "/etc/budgery.toml"

DEFAULT_CONFIG = {
	"DEBUG": True,
	"SECRET_KEY": "replace me with something good",
	"SSO_CLIENT_ID": None,
	"SSO_NAME": None,
	"SSO_OIDC_WELL_KNOWN_URL": None,
	"TESTING": False,
}

Config = Dict[str, Union[bool, int, None, str]]

class ConfigurationError(Exception):
	pass

def load() -> Config:
	"Load up the configuration"
	settings_file = os.environ.get("BUDGERY_SETTINGS", DEFAULT_CONFIG_FILE)
	config = DEFAULT_CONFIG.copy()
	try:
		with open(settings_file, "r") as c:
			from_file = toml.load(c)
			config.update(from_file)
			config.update(_get_oidc(config))
			rut
	except OSError:
		pass
	return config

def _get_oidc(config: Config) -> Config:
	"Download OpenID Connect information."
	url = config["SSO_OIDC_WELL_KNOWN_URL"]
	if not url:
		return {}
	response = requests.get(url)
	if not response.ok:
		raise ConfigurationError(f"Unable to get well-known configuration from {url}: {response.status_code} {response.text}")
	data = response.json()
	return {
		'SSO_OIDC_AUTHORIZATION_ENDPOINT': data["authorization_endpoint"],
	}

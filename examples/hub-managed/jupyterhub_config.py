import sys

c = get_config()  # noqa

c.Authenticator.admin_users = {"admin"}

c.JupyterHub.authenticator_class = "dummy"

c.JupyterHub.default_url = "/hub/home"

c.JupyterHub.load_roles = [
    {
        "name": "user",
        "scopes": ["access:services!service=announcement", "self"],
    }
]

c.JupyterHub.services = [
    {
        "name": "announcement",
        "url": "http://127.0.0.1:8888",
        "command": [sys.executable, "-m", "jupyterhub_announcement"],
    }
]

c.JupyterHub.template_paths = ["templates"]

c.DummyAuthenticator.password = "universe"

import time
import pathlib
import pytest
import socket
import subprocess


ROOT_DIR = str(pathlib.Path(__file__).resolve().parent.parent)


@pytest.fixture(scope="session")
def jupyterhub_server(tmp_path_factory):
    jupyterhub_dir = tmp_path_factory.mktemp("jupyterhub")
    jupyterhub_config_file = jupyterhub_dir / "config.py"
    config_content = f"""
c.Application.log_level = 10

c.JupyterHub.services = [
    {{
        'name': 'announcement',
        'url': 'http://127.0.0.1:8888',
        'command': [
            "python", "-m", 
            "jupyterhub_announcement", 
            "--AnnouncementService.template_paths", "['{ROOT_DIR}/templates']"
        ],
        'oauth_no_confirm': True,
    }}
]

c.JupyterHub.load_roles = [
    {{
        "name": "user",
        "scopes": ["access:services!service=announcement", "self"],
    }}
]

c.JupyterHub.authenticator_class = 'jupyterhub.auth.DummyAuthenticator'
c.Authenticator.allow_all = True
c.Authenticator.admin_users = ['admin']

c.JupyterHub.spawner_class = 'jupyterhub.spawner.SimpleLocalProcessSpawner'
"""

    with open(jupyterhub_config_file, 'w') as f:
        f.write(config_content)

    proc = subprocess.Popen(
        [
            "jupyterhub",
            "--config",
            jupyterhub_config_file
        ],
        cwd=jupyterhub_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    # Check it started successfully with a timeout of 60s
    start = time.time()
    while not is_server_up(8000) and time.time() - start < 60:
        time.sleep(5)

    yield proc

    # Shut it down at the end of the pytest session
    proc.terminate()


def is_server_up(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    except Exception:
        return False

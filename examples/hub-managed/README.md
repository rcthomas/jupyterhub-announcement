# Hub-Managed Announcement Service Example

This directory contains files needed to set up an example deployment of
jupyterhub-announcement as a 
[hub-managed service.](https://jupyterhub.readthedocs.io/en/stable/reference/services.html#launching-a-hub-managed-service)
This means that JupyterHub will start the service up for you.
The alternative is that you manage the service yourself and only tell 
JupyterHub how to talk to it.
This example should show you the basics.

## Install JupyterHub

For this example we are going to install JupyterHub into a 
[Conda environment](https://docs.conda.io/en/latest/)
using 
[conda-forge.](https://conda-forge.org/)

    $ conda create -n env jupyterhub
    $ conda activate env

This route gets you JupyterHub plus configurable-http-proxy which is also needed.
You can use `pip` to install JupyterHub as well, you just have to also install
configurable-http-proxy somehow, generally with `npm`.
For more details, refer to 
[JupyterHub's quickstart installation instructions.](https://jupyterhub.readthedocs.io/en/stable/quickstart.html)

## Install the Announcement Service

You can use `pip` to do this step:

    $ pip install git+https://github.com/rcthomas/jupyterhub-announcement.git

This will also install the dependencies 
[aiofiles](https://pypi.org/project/aiofiles/) and
[html-sanitizer.](https://pypi.org/project/html-sanitizer/)
We'll add details later on other options like PyPI or conda-forge.

## Generate a cookie secret

You'll need to generate a cookie secret for the service next.

    $ openssl rand -hex 32 > jupyterhub-announcement-cookie-secret

JupyterHub's getting started documentation explains
[cookie secrets](https://jupyterhub.readthedocs.io/en/stable/getting-started/security-basics.html#cookie-secret)
and options for generating and configuring them.
We'll store our cookie secret as a file for the purposes of demonstration.
In production you will want to secure the cookie secret.

## Configure JupyterHub

This directory also contains a `jupyterhub_config.py` configuration file.
You shouldn't need to modify this file, but you will want to examine it.

* Defines a single admin user `admin`;
* Sets the Authenticator class to the `DummyAuthenticator` and sets a dummy
  global password (again, this is a demo);
* Defines the default URL to be `/hub/home`, because otherwise the hub will try
  to redirect you to a notebook server when you log in, and you will miss the
  whole announcement part; and
* Tells JupyterHub where it can pick up the `page.html` template that extends
  JupyterHub's base `page.html` template by adding elements for getting and 
  displaying the announcement.

Most importantly, the configuration file includes the following two settings:

    c.JupyterHub.load_roles = [{
        "name": "user",
        "scopes": ["access:services!service=announcement", "self"],
    }]

This grants users access specifically to the announcement service, under 
[JupyterHub's role-based access control (RBAC) system.](https://jupyterhub.readthedocs.io/en/stable/rbac/index.html)
And then this one:
    
    c.JupyterHub.services = [{
        'name': 'announcement',
        'url': 'http://127.0.0.1:8888',
        'command': [sys.executable, "-m", "jupyterhub_announcement"]
    }]

Tells JupyterHub how to run the service when it starts up.

## Start JupyterHub

Now you should be able to start up JupyterHub, and JupyterHub will start up
the announcement service for you.

    $ jupyterhub

In the output you should see signs that the announcement service is starting up
and that it is being proxied.
Point your browser at `https://localhost:8000` and log in as an admin.
Go to the "services" dropdown, access the announcement service, set an
announcement, etc.
Then log out and log in as a regular user (say "user") and see that you can 
access the announcements UI but not create them.

## Comments

If you run this several times you may want to delete the `jupyterhub.sqlite`
database between runs.

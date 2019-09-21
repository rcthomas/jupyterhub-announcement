
import datetime
import json
import os
import sys

from jinja2 import Environment, ChoiceLoader, FileSystemLoader, PrefixLoader
from jupyterhub.services.auth import HubAuthenticated
from jupyterhub.handlers.static import LogoHandler
from jupyterhub.utils import url_path_join
from jupyterhub._data import DATA_FILES_PATH
from tornado import escape, gen, ioloop, web

from traitlets.config import Application
from traitlets import Bool, Dict, Integer, List, Unicode, default


class _JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


class AnnouncementHandler(HubAuthenticated, web.RequestHandler):

    def initialize(self, storage):
        self.storage = storage


class AnnouncementViewHandler(AnnouncementHandler):
    """View announcements page"""

    def initialize(self, storage, fixed_message, loader):
        super().initialize(storage)
        self.fixed_message = fixed_message
        self.loader = loader
        self.env = Environment(loader=self.loader)
        self.template = self.env.get_template("index.html")


    def get(self):
        user = self.get_current_user()
        prefix = self.hub_auth.hub_prefix
        logout_url = url_path_join(prefix, "logout")
        self.write(self.template.render(user=user, 
            fixed_message=self.fixed_message,
            storage=self.storage, static_url=self.static_url,
            login_url=self.hub_auth.login_url, 
            logout_url=logout_url,
            base_url=prefix,
            no_spawner_check=True))


class AnnouncementLatestHandler(AnnouncementHandler):
    """Return the latest announcement as JSON"""

    def get(self):
        if self.storage:
            latest = self.storage[-1]
        else:
            latest = {"announcement": ""}
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(escape.utf8(json.dumps(latest, cls=_JSONEncoder)))


class AnnouncementUpdateHandler(AnnouncementHandler):
    """Update announcements page"""

    hub_users = []
    allow_admin = True

    def push(self, user, announcement=""):
        self.storage.append(dict(user=user,
            announcement=announcement,
            timestamp=datetime.datetime.now()))

    @web.authenticated
    def post(self):
        """Update announcement"""
        user = self.get_current_user()
        announcement = self.get_body_argument("announcement")
        self.push(user["name"], announcement)
        self.redirect(self.application.reverse_url("view"))


class AnnouncementService(Application):

    flags = Dict({
        'generate-config': (
            {'AnnouncementService': {'generate_config': True}},
            "Generate default config file",
        )})

    generate_config = Bool(
            False, 
            help="Generate default config file"
    ).tag(config=True)

    config_file = Unicode(
            "announcement_config.py", 
            help="Config file to load"
    ).tag(config=True)

    service_prefix = Unicode(
            os.environ.get("JUPYTERHUB_SERVICE_PREFIX", 
                "/services/announcement/"),
            help="Announcement service prefix"
    ).tag(config=True)

    port = Integer(
            8888,
            help="Port this service will listen on"
    ).tag(config=True)

    data_files_path = Unicode(
            DATA_FILES_PATH,
            help="Location of JupyterHub data files"
    ).tag(config=True)

    template_paths = List(
            help="Search paths for jinja templates, coming before default ones"
    ).tag(config=True)

    @default('template_paths')
    def _template_paths_default(self):
        return [os.path.join(self.data_files_path, 'announcement/templates'),
                os.path.join(self.data_files_path, 'templates')]

    logo_file = Unicode(
            "",
            help="Logo path, can be used to override JupyterHub one",
    ).tag(config=True)

    @default('logo_file')
    def _logo_file_default(self):
        return os.path.join(
            self.data_files_path, 'static', 'images', 'jupyterhub-80.png'
        )

    fixed_message = Unicode(
            "",
            help="""Fixed message to show at the top of the page.

            A good use for this parameter would be a link to a more general
            live system status page or MOTD."""
    ).tag(config=True)

    def initialize(self, argv=None):
        super().initialize(argv)
        if self.generate_config:
            print(self.generate_config_file())
            sys.exit(0)

        if self.config_file:
            self.load_config_file(self.config_file)

        self.storage = list()

        base_path = self._template_paths_default()[0]
        if base_path not in self.template_paths:
            self.template_paths.append(base_path)
        loader = ChoiceLoader(
            [
                PrefixLoader({'templates': FileSystemLoader([base_path])}, '/'),
                FileSystemLoader(self.template_paths),
            ]
        )

        self.settings = {
                "static_path": os.path.join(self.data_files_path, "static"),
                "static_url_prefix": url_path_join(self.service_prefix, "static/")
        }

        self.app = web.Application([
            (self.service_prefix, AnnouncementViewHandler, dict(storage=self.storage, fixed_message=self.fixed_message, loader=loader), "view"),
            (self.service_prefix + r"latest", AnnouncementLatestHandler, dict(storage=self.storage)),
            (self.service_prefix + r"update", AnnouncementUpdateHandler, dict(storage=self.storage)),
            (self.service_prefix + r"static/(.*)", web.StaticFileHandler, dict(path=self.settings["static_path"])),
            (self.service_prefix + r"logo", LogoHandler, {"path": self.logo_file})
        ], **self.settings)

    def start(self):
        self.app.listen(self.port)
        ioloop.IOLoop.current().start()


def main():
    app = AnnouncementService()
    app.initialize()
    app.start()

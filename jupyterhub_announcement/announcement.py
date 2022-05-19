import binascii
import json
import os
import sys

from html_sanitizer import Sanitizer
from jinja2 import ChoiceLoader, Environment, FileSystemLoader, PrefixLoader
from jupyterhub._data import DATA_FILES_PATH
from jupyterhub.handlers.static import LogoHandler
from jupyterhub.services.auth import HubOAuthCallbackHandler, HubOAuthenticated
from jupyterhub.utils import url_path_join
from tornado import escape, gen, ioloop, web
from traitlets import Any, Bool, Dict, Integer, List, Unicode, default
from traitlets.config import Application

from jupyterhub_announcement.encoder import _JSONEncoder
from jupyterhub_announcement.queue import AnnouncementQueue
from jupyterhub_announcement.ssl import SSLContext


class AnnouncementHandler(HubOAuthenticated, web.RequestHandler):
    def initialize(self, queue):
        self.queue = queue


class AnnouncementViewHandler(AnnouncementHandler):
    """View announcements page"""

    def initialize(self, queue, fixed_message, loader):
        super().initialize(queue)
        self.fixed_message = fixed_message
        self.loader = loader
        self.env = Environment(loader=self.loader)
        self.template = self.env.get_template("index.html")

    @web.authenticated
    def get(self):
        user = self.get_current_user()
        prefix = self.hub_auth.hub_prefix
        logout_url = url_path_join(prefix, "logout")
        self.write(
            self.template.render(
                user=user,
                fixed_message=self.fixed_message,
                announcements=self.queue.announcements,
                static_url=self.static_url,
                login_url=self.hub_auth.login_url,
                logout_url=logout_url,
                base_url=prefix,
                no_spawner_check=True,
            )
        )


class AnnouncementLatestHandler(AnnouncementHandler):
    """Return the latest announcement as JSON"""

    def initialize(self, queue, allow_origin):
        super().initialize(queue)
        self.allow_origin = allow_origin

    def get(self):
        latest = {"announcement": ""}
        if self.queue.announcements:
            latest = self.queue.announcements[-1]
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        if self.allow_origin:
            self.add_header("Access-Control-Allow-Headers", "Content-Type")
            self.add_header("Access-Control-Allow-Origin", "*")
            self.add_header("Access-Control-Allow-Methods", "OPTIONS,GET")
        self.write(escape.utf8(json.dumps(latest, cls=_JSONEncoder)))


class AnnouncementUpdateHandler(AnnouncementHandler):
    """Update announcements page"""

    hub_users = []
    allow_admin = True

    @web.authenticated
    async def post(self):
        """Update announcement"""
        user = self.get_current_user()
        sanitizer = Sanitizer()
        # announcement = self.get_body_argument("announcement")
        announcement = sanitizer.sanitize(self.get_body_argument("announcement"))
        await self.queue.update(user["name"], announcement)
        self.redirect(self.application.reverse_url("view"))


class AnnouncementService(Application):

    classes = [AnnouncementQueue, SSLContext]

    flags = Dict(
        {
            "generate-config": (
                {"AnnouncementService": {"generate_config": True}},
                "Generate default config file",
            )
        }
    )

    generate_config = Bool(False, help="Generate default config file").tag(config=True)

    config_file = Unicode("announcement_config.py", help="Config file to load").tag(
        config=True
    )

    service_prefix = Unicode(
        os.environ.get("JUPYTERHUB_SERVICE_PREFIX", "/services/announcement/"),
        help="Announcement service prefix",
    ).tag(config=True)

    port = Integer(8888, help="Port this service will listen on").tag(config=True)

    allow_origin = Bool(False, help="Allow access from subdomains").tag(config=True)

    data_files_path = Unicode(DATA_FILES_PATH, help="Location of JupyterHub data files")

    template_paths = List(
        help="Search paths for jinja templates, coming before default ones"
    ).tag(config=True)

    @default("template_paths")
    def _template_paths_default(self):
        return [
            os.path.join(self.data_files_path, "announcement/templates"),
            os.path.join(self.data_files_path, "templates"),
        ]

    logo_file = Unicode(
        "",
        help="Logo path, can be used to override JupyterHub one",
    ).tag(config=True)

    @default("logo_file")
    def _logo_file_default(self):
        return os.path.join(
            self.data_files_path, "static", "images", "jupyterhub-80.png"
        )

    fixed_message = Unicode(
        "",
        help="""Fixed message to show at the top of the page.

         A good use for this parameter would be a link to a more general
         live system status page or MOTD.""",
    ).tag(config=True)

    ssl_context = Any()

    cookie_secret_file = Unicode(
        "jupyterhub-announcement-cookie-secret",
        help="File in which we store the cookie secret.",
    ).tag(config=True)

    def initialize(self, argv=None):
        super().initialize(argv)

        if self.generate_config:
            print(self.generate_config_file())
            sys.exit(0)

        if self.config_file:
            self.load_config_file(self.config_file)

        # Totally confused by traitlets logging
        self.log.parent.setLevel(self.log.level)

        self.init_queue()
        self.init_ssl_context()

        base_path = self._template_paths_default()[0]
        if base_path not in self.template_paths:
            self.template_paths.append(base_path)
        loader = ChoiceLoader(
            [
                PrefixLoader({"templates": FileSystemLoader([base_path])}, "/"),
                FileSystemLoader(self.template_paths),
            ]
        )

        with open(self.cookie_secret_file) as f:
            cookie_secret_text = f.read().strip()
        cookie_secret = binascii.a2b_hex(cookie_secret_text)

        self.settings = {
            "cookie_secret": cookie_secret,
            "static_path": os.path.join(self.data_files_path, "static"),
            "static_url_prefix": url_path_join(self.service_prefix, "static/"),
        }

        self.app = web.Application(
            [
                (
                    self.service_prefix,
                    AnnouncementViewHandler,
                    dict(
                        queue=self.queue,
                        fixed_message=self.fixed_message,
                        loader=loader,
                    ),
                    "view",
                ),
                (self.service_prefix + r"oauth_callback", HubOAuthCallbackHandler),
                (
                    self.service_prefix + r"latest",
                    AnnouncementLatestHandler,
                    dict(queue=self.queue, allow_origin=self.allow_origin),
                ),
                (
                    self.service_prefix + r"update",
                    AnnouncementUpdateHandler,
                    dict(queue=self.queue),
                ),
                (
                    self.service_prefix + r"static/(.*)",
                    web.StaticFileHandler,
                    dict(path=self.settings["static_path"]),
                ),
                (self.service_prefix + r"logo", LogoHandler, {"path": self.logo_file}),
            ],
            **self.settings,
        )

    def init_queue(self):
        self.queue = AnnouncementQueue(log=self.log, config=self.config)

    def init_ssl_context(self):
        self.ssl_context = SSLContext(config=self.config).ssl_context()

    def start(self):
        self.app.listen(self.port, ssl_options=self.ssl_context)

        async def purge_loop():
            await self.queue.purge()
            await gen.sleep(300)

        ioloop.IOLoop.current().add_callback(purge_loop)
        ioloop.IOLoop.current().start()


def main():
    app = AnnouncementService()
    app.initialize()
    app.start()

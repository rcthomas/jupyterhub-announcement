
import datetime
import json
import os
import sys

from jinja2 import Environment, ChoiceLoader, FileSystemLoader, PrefixLoader
from jupyterhub.services.auth import HubAuthenticated
from jupyterhub.handlers.static import LogoHandler
from jupyterhub.utils import url_path_join, make_ssl_context
from jupyterhub._data import DATA_FILES_PATH
from tornado import escape, gen, ioloop, web

from traitlets.config import Application, Configurable, LoggingConfigurable
from traitlets import Any, Bool, Dict, Float, Integer, List, Unicode, default

from html_sanitizer import Sanitizer

class _JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


def _datetime_hook(json_dict):
    for (key, value) in json_dict.items():
        try:
            json_dict[key] = datetime.datetime.fromisoformat(value)
        except:
            pass
    return json_dict


class AnnouncementQueue(LoggingConfigurable):

    announcements = List()

    persist_path = Unicode(
            "",
            help="""File path where announcements persist as JSON.

            For a persistent announcement queue, this parameter must be set to
            a non-empty value and correspond to a read+write-accessible path.
            The announcement queue is stored as a list of JSON objects. If this
            parameter is set to a non-empty value:

            * The persistence file is used to initialize the announcement queue
              at start-up. This is the only time the persistence file is read.
            * If the persistence file does not exist at start-up, it is
              created when an announcement is added to the queue.
            * The persistence file is over-written with the contents of the
              announcement queue each time a new announcement is added.

            If this parameter is set to an empty value (the default) then the
            queue is just empty at initialization and the queue is ephemeral;
            announcements will not be persisted on updates to the queue."""
    ).tag(config=True)

    lifetime_days = Float(7.0,
            help="""Number of days to retain announcements.

            Announcements that have been in the queue for this many days are
            purged from the queue."""
    ).tag(config=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if self.persist_path:
            self.log.info(f"restoring queue from {self.persist_path}")
            self._handle_restore()
        else:
            self.log.info("ephemeral queue, persist_path not set")
        self.log.info(f"queue has {len(self.announcements)} announcements")

    def _handle_restore(self):
        try:
            self._restore()
        except FileNotFoundError:
            self.log.info(f"persist_path not found ({self.persist_path})")
        except Exception as err:
            self.log.error(f"failed to restore queue ({err})")

    def _restore(self):
        with open(self.persist_path, "r") as stream:
            self.announcements = json.load(stream, object_hook=_datetime_hook)

    def update(self, user, announcement=""):
        self.announcements.append(dict(user=user,
            announcement=announcement,
            timestamp=datetime.datetime.now()))
        if self.persist_path:
            self.log.info(f"persisting queue to {self.persist_path}")
            self._handle_persist()

    def _handle_persist(self):
        try:
            self._persist()
        except Exception as err:
            self.log.error(f"failed to persist queue ({err})")

    def _persist(self):
        with open(self.persist_path, "w") as stream:
            json.dump(self.announcements, stream, cls=_JSONEncoder, indent=2)

    def purge(self):
        max_age = datetime.timedelta(days=self.lifetime_days)
        now = datetime.datetime.now()
        old_count = len(self.announcements)
        self.announcements = [a for a in self.announcements 
                if now - a["timestamp"] < max_age]
        if self.persist_path and len(self.announcements) < old_count:
            self.log.info(f"persisting queue to {self.persist_path}")
            self._handle_persist()


class AnnouncementHandler(HubAuthenticated, web.RequestHandler):

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


    def get(self):
        user = self.get_current_user()
        prefix = self.hub_auth.hub_prefix
        logout_url = url_path_join(prefix, "logout")
        self.write(self.template.render(user=user, 
            fixed_message=self.fixed_message,
            announcements=self.queue.announcements,
            static_url=self.static_url,
            login_url=self.hub_auth.login_url, 
            logout_url=logout_url,
            base_url=prefix,
            no_spawner_check=True))


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
            self.add_header("Access-Control-Allow-Methods", 'OPTIONS,GET')
        self.write(escape.utf8(json.dumps(latest, cls=_JSONEncoder)))


class AnnouncementUpdateHandler(AnnouncementHandler):
    """Update announcements page"""

    hub_users = []
    allow_admin = True

    @web.authenticated
    def post(self):
        """Update announcement"""
        user = self.get_current_user()
        sanitizer = Sanitizer()
        # announcement = self.get_body_argument("announcement")
        announcement = sanitizer.sanitize(self.get_body_argument("announcement"))
        self.queue.update(user["name"], announcement)
        self.redirect(self.application.reverse_url("view"))


class SSLContext(Configurable):
    
    keyfile = Unicode(
            os.getenv("JUPYTERHUB_SSL_KEYFILE", ""),
            help="SSL key, use with certfile"
    ).tag(config=True)

    certfile = Unicode(
            os.getenv("JUPYTERHUB_SSL_CERTFILE", ""),
            help="SSL cert, use with keyfile"
    ).tag(config=True)

    cafile = Unicode(
            os.getenv("JUPYTERHUB_SSL_CLIENT_CA", ""),
            help="SSL CA, use with keyfile and certfile"
    ).tag(config=True)

    def ssl_context(self):  
        if self.keyfile and self.certfile and self.cafile:
            return make_ssl_context(self.keyfile, self.certfile,
                    cafile=self.cafile, check_hostname=False)
        else:
            return None


class AnnouncementService(Application):

    classes = [AnnouncementQueue, SSLContext]

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

    allow_origin = Bool(
        False,
        help="Allow access from subdomains"
    ).tag(config=True)

    data_files_path = Unicode(
            DATA_FILES_PATH,
            help="Location of JupyterHub data files"
    )

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

    ssl_context = Any()

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
                PrefixLoader({'templates': FileSystemLoader([base_path])}, '/'),
                FileSystemLoader(self.template_paths),
            ]
        )

        self.settings = {
                "static_path": os.path.join(self.data_files_path, "static"),
                "static_url_prefix": url_path_join(self.service_prefix, "static/")
        }

        self.app = web.Application([
            (self.service_prefix, AnnouncementViewHandler, dict(queue=self.queue, fixed_message=self.fixed_message, loader=loader), "view"),
            (self.service_prefix + r"latest", AnnouncementLatestHandler, dict(queue=self.queue, allow_origin=self.allow_origin)),
            (self.service_prefix + r"update", AnnouncementUpdateHandler, dict(queue=self.queue)),
            (self.service_prefix + r"static/(.*)", web.StaticFileHandler, dict(path=self.settings["static_path"])),
            (self.service_prefix + r"logo", LogoHandler, {"path": self.logo_file})
        ], **self.settings)

    def init_queue(self):
        self.queue = AnnouncementQueue(log=self.log, config=self.config)

    def init_ssl_context(self):
        self.ssl_context = SSLContext(config=self.config).ssl_context()

    def start(self):
        self.app.listen(self.port, ssl_options=self.ssl_context)
        def purge_callback():
            self.queue.purge()
        c = ioloop.PeriodicCallback(purge_callback, 300000)
        c.start()
        ioloop.IOLoop.current().start()


def main():
    app = AnnouncementService()
    app.initialize()
    app.start()

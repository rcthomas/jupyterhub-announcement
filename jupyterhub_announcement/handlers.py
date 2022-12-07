import json
import logging

from html_sanitizer import Sanitizer
from jinja2 import Environment
from jupyterhub.services.auth import HubOAuthenticated
from jupyterhub.utils import url_path_join
from tornado import escape, web

from jupyterhub_announcement.encoder import _JSONEncoder


class AnnouncementHandler(HubOAuthenticated, web.RequestHandler):
    def initialize(self, queue):
        super().initialize()
        self.queue = queue

    @property
    def log(self):
        return self.settings.get("log", logging.getLogger("tornado.application"))


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
                parsed_scopes=user.get("hub_scopes") or [],
            )
        )


class AnnouncementOutputHandler(AnnouncementHandler):
    def write_output(self, output):
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        if self.allow_origin:
            self.add_header("Access-Control-Allow-Headers", "Content-Type")
            self.add_header("Access-Control-Allow-Origin", "*")
            self.add_header("Access-Control-Allow-Methods", "OPTIONS,GET")
        self.write(escape.utf8(json.dumps(output, cls=_JSONEncoder)))


class AnnouncementLatestHandler(AnnouncementOutputHandler):
    """Return the latest announcement as JSON"""

    def initialize(self, queue, allow_origin, extra_info_hook):
        super().initialize(queue)
        self.allow_origin = allow_origin
        self.extra_info_hook = extra_info_hook



    async def get(self):
        latest = {"announcement": ""}
        if self.queue.announcements:
            latest = dict(self.queue.announcements[-1])
        query_extra = self.get_query_argument("extra", "none").lower()
        if self.extra_info_hook and (query_extra in ["separate", "combined"]):
            extra_info = await self.extra_info_hook(self)
            if query_extra == "separate":
                latest["extra"] = extra_info
            if query_extra == "combined" and extra_info:
                if latest["announcement"]:
                    latest["announcement"] += "<br>" + extra_info
                else:
                    latest["announcement"] = extra_info
        self.write_output(latest)


class AnnouncementListHandler(AnnouncementOutputHandler):
    """Return the latest announcement as JSON"""

    def initialize(self, queue, allow_origin, default_limit=5):
        super().initialize(queue)
        self.allow_origin = allow_origin
        self.default_limit = default_limit

    async def get(self):
        output = []
        limit = int(self.get_argument("limit", self.default_limit))
        if self.queue.announcements:
            output = [dict(a) for a in self.queue.announcements[-limit:]]
        self.write_output(output)


class AnnouncementUpdateHandler(AnnouncementHandler):
    """Update announcements page"""

    hub_users = []
    allow_admin = True

    @web.authenticated
    async def post(self):
        """Update announcement"""
        user = self.get_current_user()
        sanitizer = Sanitizer()
        announcement = sanitizer.sanitize(self.get_body_argument("announcement"))
        await self.queue.update(user["name"], announcement)
        self.redirect(self.application.reverse_url("view"))

import datetime
import json

import aiofiles
from traitlets import Float, List, Unicode
from traitlets.config import LoggingConfigurable

from jupyterhub_announcement.encoder import _JSONEncoder


def _datetime_hook(json_dict):
    for (key, value) in json_dict.items():
        try:
            json_dict[key] = datetime.datetime.fromisoformat(value)
        except Exception:
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
        announcements will not be persisted on updates to the queue.""",
    ).tag(config=True)

    lifetime_days = Float(
        7.0,
        help="""Number of days to retain announcements.

        Announcements that have been in the queue for this many days are
        purged from the queue.""",
    ).tag(config=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if self.persist_path:
            self.log.info(f"restoring queue from {self.persist_path}")
            self._handle_restore()
        else:
            self.log.info("ephemeral queue, persist_path not set")
        self.log.info(f"queue has {len(self.announcements)} announcements")

    def __len__(self):
        return len(self.announcements)

    def _handle_restore(self):
        try:
            self._restore()
        except FileNotFoundError:
            self.log.info(f"persist_path not found ({self.persist_path})")
        except Exception as err:
            self.log.error(f"failed to restore queue ({err})")

    def _restore(self):
        with open(self.persist_path) as stream:
            self.announcements = json.load(stream, object_hook=_datetime_hook)

    async def update(self, user, announcement=""):
        self.announcements.append(
            dict(
                user=user, announcement=announcement, timestamp=datetime.datetime.now()
            )
        )
        if self.persist_path:
            self.log.info(f"persisting queue to {self.persist_path}")
            await self._handle_persist()

    async def _handle_persist(self):
        try:
            await self._persist()
        except Exception as err:
            self.log.error(f"failed to persist queue ({err})")

    async def _persist(self):
        async with aiofiles.open(self.persist_path, "w") as stream:
            await stream.write(
                json.dumps(self.announcements, cls=_JSONEncoder, indent=2)
            )

    async def purge(self):
        max_age = datetime.timedelta(days=self.lifetime_days)
        now = datetime.datetime.now()
        old_count = len(self.announcements)
        self.announcements = [
            a for a in self.announcements if now - a["timestamp"] < max_age
        ]
        if self.persist_path and len(self.announcements) < old_count:
            self.log.info(f"persisting queue to {self.persist_path}")
            await self._handle_persist()

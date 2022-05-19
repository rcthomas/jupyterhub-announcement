import time

import pytest

from jupyterhub_announcement.queue import AnnouncementQueue


@pytest.fixture
def announcement():
    yield ("user1", "hello world")


@pytest.fixture
def lifetime_days_2s():
    yield 2.0 / 86400.0


@pytest.mark.asyncio
async def test_queue_default(announcement):
    queue = AnnouncementQueue()

    # Defaults are set

    assert len(queue) == 0
    assert queue.persist_path == ""
    assert queue.lifetime_days == pytest.approx(7.0)

    # Updating adds announcement

    await queue.update(*announcement)
    assert len(queue) == 1
    assert queue.announcements[0]["user"] == announcement[0]
    assert queue.announcements[0]["announcement"] == announcement[1]

    # Updating again adds yet another with a later timestamp

    await queue.update(*announcement)
    assert len(queue) == 2
    assert queue.announcements[1]["timestamp"] > queue.announcements[0]["timestamp"]

    # Unless the test takes a log time, purge should have no effect here

    await queue.purge()
    assert len(queue) == 2


@pytest.mark.asyncio
async def test_queue_persistent(announcement, tmp_path):
    persist_path = str(tmp_path / "announcements.json")

    queue = AnnouncementQueue(persist_path=persist_path)

    # Persist path is set

    assert queue.persist_path == persist_path

    # Update queue

    await queue.update(*announcement)

    # Drop the queue, make new one and verify the announcement is there

    del queue
    new_queue = AnnouncementQueue(persist_path=persist_path)
    assert len(new_queue) == 1
    assert new_queue.announcements[0]["user"] == announcement[0]
    assert new_queue.announcements[0]["announcement"] == announcement[1]


@pytest.mark.asyncio
async def test_queue_purge(announcement, tmp_path, lifetime_days_2s):
    persist_path = str(tmp_path / "announcements.json")

    queue = AnnouncementQueue(persist_path=persist_path, lifetime_days=lifetime_days_2s)

    # Update queue and purge immediately without effect

    await queue.update(*announcement)
    await queue.purge()
    assert len(queue) == 1

    # Wait until after purge and verify old message disappeared

    time.sleep(5)
    await queue.purge()
    assert len(queue) == 0

    # Drop the queue, make new one, should be no message

    del queue
    new_queue = AnnouncementQueue(persist_path=persist_path)
    assert len(new_queue) == 0


def test_queue_restore_fail(tmp_path):

    # Failure to restore isn't fatal, the queue is just empty

    persist_path = tmp_path / "announcements.json"
    persist_path.write_text("not json")
    queue = AnnouncementQueue(persist_path=str(persist_path))
    assert len(queue) == 0


@pytest.mark.asyncio
async def test_queue_persist_fail(tmp_path, announcement):
    class Whatever:
        pass

    # Failure to persist isn't fatal just keep going

    persist_path = str(tmp_path / "announcements.json")
    queue = AnnouncementQueue(persist_path=persist_path)
    await queue.update(*announcement)
    queue.announcements[0]["other"] = Whatever()
    try:
        await queue._handle_persist()
    except Exception as err:
        assert False, f"'_handle_persist' raised exception {err}"

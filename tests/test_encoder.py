import datetime
import json

import pytest

from jupyterhub_announcement.encoder import _JSONEncoder


@pytest.fixture
def timestamp():
    yield datetime.datetime(2022, 5, 17, 16, 59, 23, 123456)


@pytest.fixture
def good_document(timestamp):
    yield {
        "user": "falken",
        "announcement": "Wouldn't you like to play a nice game of chess?",
        "timestamp": timestamp,
    }


@pytest.fixture
def bad_document(timestamp):
    class Whatever:
        pass

    yield {
        "user": "falken",
        "announcement": "Wouldn't you like to play a nice game of chess?",
        "timestamp": timestamp,
        "other": Whatever(),
    }


def test_json_encoder_good(good_document, timestamp):
    string = json.dumps(good_document, cls=_JSONEncoder)
    parsed = json.loads(string)

    assert not (set(parsed.keys()) - set(good_document.keys()))
    for key in good_document:
        if key == "timestamp":
            assert parsed[key] == timestamp.isoformat()
        else:
            assert parsed[key] == good_document[key]


def test_json_encoder_bad(bad_document, timestamp):
    with pytest.raises(TypeError):
        json.dumps(bad_document, cls=_JSONEncoder)

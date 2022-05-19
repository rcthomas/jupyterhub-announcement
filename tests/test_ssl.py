import ssl

import pytest
from certipy import Certipy

from jupyterhub_announcement.ssl import SSLContext


@pytest.fixture
def ca():
    yield "foo"


@pytest.fixture
def keypair():
    yield "bar"


@pytest.fixture
def certs_record(tmp_path, ca, keypair):
    certipy = Certipy(store_dir=tmp_path)
    certipy.create_ca(ca)
    yield certipy.create_signed_pair(keypair, ca)


def test_none():
    context = SSLContext()
    assert context.ssl_context() is None


def test_whatever(certs_record):
    files = certs_record["files"]
    context = SSLContext(
        keyfile=files["key"], certfile=files["cert"], cafile=files["ca"]
    )
    assert type(context.ssl_context()) == ssl.SSLContext

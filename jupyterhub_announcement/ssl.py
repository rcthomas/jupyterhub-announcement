import os

from jupyterhub.utils import make_ssl_context
from traitlets import Unicode
from traitlets.config import Configurable


class SSLContext(Configurable):

    keyfile = Unicode(
        os.getenv("JUPYTERHUB_SSL_KEYFILE", ""), help="SSL key, use with certfile"
    ).tag(config=True)

    certfile = Unicode(
        os.getenv("JUPYTERHUB_SSL_CERTFILE", ""), help="SSL cert, use with keyfile"
    ).tag(config=True)

    cafile = Unicode(
        os.getenv("JUPYTERHUB_SSL_CLIENT_CA", ""),
        help="SSL CA, use with keyfile and certfile",
    ).tag(config=True)

    def ssl_context(self):
        if self.keyfile and self.certfile and self.cafile:
            return make_ssl_context(
                self.keyfile, self.certfile, cafile=self.cafile, check_hostname=False
            )
        else:
            return None

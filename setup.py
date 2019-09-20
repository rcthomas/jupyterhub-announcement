#!/usr/bin/env python

from distutils.core import setup

setup(
        name='jupyterhub-announcement',
        version='0.0.1',
        description='JupyterHub Announcement Service',
        author='R. C. Thomas',
        author_email='rcthomas@lbl.gov',
        packages=['jupyterhub_announcement'],
        data_files=[("share/jupyterhub/announcement/templates", 
            ["templates/index.html"])]
)

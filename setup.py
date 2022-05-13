from setuptools import setup

setup(
    author='R. C. Thomas, François Tessier',
    author_email='rcthomas@lbl.gov',
    data_files=[
        ("share/jupyterhub/announcement/templates", ["templates/index.html"])
    ],
    description='JupyterHub Announcement Service',
    install_requires=[
        "aiofiles",
        "html-sanitizer",
        "jupyterhub",
    ],
    name='jupyterhub-announcement',
    packages=['jupyterhub_announcement'],
    version='0.8.0.dev',
)

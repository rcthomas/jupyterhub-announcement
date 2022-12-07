from pathlib import Path

from setuptools import setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    author="R. C. Thomas, François Tessier, Narek Amirbekian",
    author_email="rcthomas@lbl.gov",
    data_files=[("share/jupyterhub/announcement/templates", ["templates/index.html"])],
    description="JupyterHub Announcement Service",
    install_requires=open("requirements.txt").read().splitlines(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    name="jupyterhub-announcement",
    packages=["jupyterhub_announcement"],
    url="https://github.com/rcthomas/jupyterhub-announcement",
    version="0.9.0",
)

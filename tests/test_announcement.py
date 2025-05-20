import os
import subprocess
import requests
import pytest


@pytest.mark.parametrize("user", ["normal", "admin"])
def test_api_resources(jupyterhub_server, user):
    """Test to check if announcement endpoints are working"""
    # Auth data
    auth_payload = {
        'username': user,
        'password': 'pass',
    }
    # Announcement data
    announcement_payload = {
        'announcement': 'This is test announcement',
    }

    # Open a session to login and test API resources
    with requests.Session() as session:
        # Go to login page to fetch XSRF token
        login = session.get("http://localhost:8000/hub/login")
        assert login.status_code == 200

        # Get XSRF session cookie and update payload
        cookie = login.cookies['_xsrf']
        auth_payload.update({
            '_xsrf': cookie
        })

        # Login into hub
        auth = session.post("http://localhost:8000/hub/login", data=auth_payload)
        assert auth.status_code == 200

        # Goto announcements page
        announcement = session.get(
            f"http://localhost:8000/services/announcement/"
        )
        assert announcement.status_code == 200

        # Get latest announcement
        latest = session.get(
            f"http://localhost:8000/services/announcement/latest"
        )
        assert latest.status_code == 200

        # Get XSRF cookie for announcement service. These cookies are
        # tied to path so we cannot use cookie of /hub/home
        cookie = session.cookies.get(name='_xsrf', path='/services/announcement/')

        # Make a post request to update announcement. Should be 403 for regular
        # user and 200 for admin user
        announcement = session.post(
            f"http://localhost:8000/services/announcement/update?_xsrf={cookie}",
            data=announcement_payload,
        )
        if user == 'admin':
            expected = 200
        else:
            expected = 403
        assert announcement.status_code == expected

from datetime import datetime, timedelta

import pytest

from bbapilib import BBClient, BBSession, BBAuth

@pytest.fixture
def client():
    auth = BBAuth("", "", "")
    auth.token = "TOKEN", "VALIDO"
    client = BBClient(BBSession(auth))
    return client

@pytest.fixture
def client_authenticated():
    auth = BBAuth("", "", "")
    auth._token = "TOKEN", "VALIDO"
    auth.expires_in = datetime.now() + timedelta(seconds=600)
    client = BBClient(BBSession(auth))
    return client
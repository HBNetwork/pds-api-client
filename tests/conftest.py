import pytest

from bbapilib import BBClient, BBSession, BBAuth

@pytest.fixture
def client():
    auth = BBAuth("", "", "")
    auth.token = "TOKEN", "VALIDO"
    client = BBClient(BBSession(auth))
    return client
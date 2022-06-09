import pytest
import responses
import requests

from bbapilib import BBAuthSandbox, BadCredentials

URL = "https://oauth.sandbox.bb.com.br/oauth/token"

@pytest.fixture
def auth():
    client_id = "xxx"
    client_secret = "xxx"
    developer_key = "xxx"
    auth = BBAuthSandbox(client_id, client_secret, developer_key)
    return auth


def test_token_initial_none(auth):
    assert auth._token is None


@responses.activate
def test_generate_token(auth):
    responses.add(
        responses.POST,
        URL,
        json={"access_token": "123", "token_type": "Bearer"}
    )

    requests.post(URL, auth=auth)

    assert auth.token == "Bearer 123"


def test_renew_data(auth, mocker):
    mock = mocker.patch("requests.post")
    data = {
        'grant_type': 'client_credentials',
        'code': auth.developer_key,
    }

    auth.renew()

    mock.assert_called_with(URL, data=data, verify=False, auth=auth.credentials)

@responses.activate
def test_bad_credentials(auth):
    responses.add(
        responses.POST,
        URL,
        status=401
    )

    with pytest.raises(BadCredentials):
        auth.renew()
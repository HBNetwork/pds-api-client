from datetime import datetime, timedelta

import pytest
import responses
import requests
from requests import Response

from bbapilib import BBAuthSandbox, BadCredentials, BBAuth

URL = "https://oauth.sandbox.bb.com.br/oauth/token"
URL_SERVICE = "https://api.bb.com/pix/v1/"


@pytest.fixture
def auth():
    client_id = "id"
    client_secret = "secret"
    developer_key = "key"
    return BBAuthSandbox(client_id, client_secret, developer_key)

def test_token_initial_none(auth):
    assert auth._token is None


@responses.activate
def test_generate_token(auth):
    responses.add(
        responses.POST,
        URL,
        json={"access_token": "123", "token_type": "Bearer", "expires_in": 600}
    )
    responses.add(
        responses.GET,
        URL_SERVICE,
        json={"data": "Worked"}
    )

    r = requests.get(URL_SERVICE, auth=auth)

    assert r.request.headers["Authorization"] == "Bearer 123"


@responses.activate
def test_developer_key(auth):
    responses.add(
        responses.POST,
        URL,
        json={"access_token": "123", "token_type": "Bearer", "expires_in": 600}
    )
    responses.add(
        responses.GET,
        URL_SERVICE,
        json={"data": "Worked"}
    )

    r = requests.get(URL_SERVICE, auth=auth)

    assert r.request.headers["x-developer-application-key"] == "key"



@responses.activate
def test_bad_credentials(auth):
    responses.add(
        responses.POST,
        URL,
        status=401
    )

    with pytest.raises(BadCredentials):
        auth.renew()


@responses.activate
def test_renew_expired_token(auth):
    responses.add(
        responses.POST,
        URL,
        json={"access_token": "new_access_token", "token_type": "Bearer", "expires_in": 600}
    )
    responses.add(
        responses.GET,
        URL_SERVICE,
        json={"data": "Worked"}
    )

    now = datetime.now()
    before = now - timedelta(seconds=600)
    auth._token = 'old_token'
    auth.expires_in = before

    r = requests.get(URL_SERVICE, auth=auth)

    assert r.request.headers["Authorization"] == "Bearer new_access_token"

    # Auth tem um token válido
    # O token expira pelo tempo.
    # tento fazer uma request
    # tem que renovar o token
    # Faz a requisção novamente.
    # valida sucesso


@responses.activate
def test_replay_request_when_expires_token(auth):
    auth._token = '123'
    auth.expires_in = datetime.now() + timedelta(seconds=600)

    responses.add(
        responses.GET,
        URL_SERVICE,
        json={"statusCode": 401, "error": "Unauthorized", "message": "Bad Credentials",
              "attributes": {"error": "Bad Credentials"}},
        status=401
    )
    responses.add(
        responses.POST,
        URL,
        json={"access_token": "new_access_token", "token_type": "Bearer", "expires_in": 600}
    )
    responses.add(
        responses.GET,
        URL_SERVICE,
        json={'data': 'worked'}
    )

    resp = requests.get(URL_SERVICE, auth=auth)
    json = resp.json()

    assert len(responses.calls) == 3
    assert responses.calls[2].request.url == URL_SERVICE
    assert json['data'] == 'worked'

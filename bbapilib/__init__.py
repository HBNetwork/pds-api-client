# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import base64
from pprint import pprint

import requests
from requests.auth import AuthBase, HTTPBasicAuth


class BBAuth(AuthBase):
    OAUTH_ENDPOINT = "https://oauth.bb.com.br/oauth/token"

    def __init__(self, client_id, client_secret, developer_key):
        # super(BBAuthBaseHomologacao, self).__init__(client_id, client_secret)
        self.client_id = client_id
        self.client_secret = client_secret
        self.developer_key = developer_key
        self._token = None
        self.credentials = (client_id, client_secret)

    @property
    def token(self):
        if not self._token:
            self.renew()
        return self._token

    def renew(self):
        data = {
            'grant_type': 'client_credentials',
            'code': self.developer_key,
        }

        resp = requests.post(self.OAUTH_ENDPOINT, data=data, verify=False, auth=self.credentials)

        json_resp = resp.json()

        token = json_resp['access_token']
        token_type = json_resp['token_type']
        self._token = f'{token_type} {token}'

    def __call__(self, r):
        r.headers['Authorization'] = self.token
        r.headers['x-developer-application-key'] = self.developer_key
        print(self.token)
        return r


class BBAuthSandbox(BBAuth):
    OAUTH_ENDPOINT = "https://oauth.sandbox.bb.com.br/oauth/token"


class BBSession(requests.Session):
    _host = 'sandbox.bb.com.br'
    _endpoint = None
    _header = None
    _client_id = None
    _client_secret = None
    _developer_key = None

    def __init__(self, client_id: str, cliente_secret: str, developer_key: str):
        super(BBSession, self).__init__()
        self._endpoint = f"https://api.{self._host}/pix/v1/"
        self._client_secret = cliente_secret
        self._client_id = client_id
        self._developer_key = developer_key

    def request(self, method: str, path='', *args, **kwargs):

        url = f'{self._endpoint}{path}'

        if self._header is None:
            self.authenticate()

        resp = super(BBSession, self).request(method, url, *args, headers=self._header, verify=False, **kwargs)

        return resp

    def generate_basic_auth_token(self):
        text = self._client_id + ":" + self._client_secret
        return base64.b64encode(text.encode('ascii')).decode('ascii')

    def authenticate(self):

        url_oauth = f"https://oauth.{self._host}/oauth/token"

        headers = {
            'Authorization': "Basic " + self.generate_basic_auth_token(),
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        data = {
            'grant_type': 'client_credentials',
            'code': self._developer_key,

        }

        resp = super(BBSession, self).request('post', url_oauth, data=data, headers=headers, verify=False)

        json_resp = resp.json()

        access_token = json_resp['access_token']

        self._header = {
            'Authorization': 'Bearer ' + access_token,
            # Mesmo na produção é para usar esse
            'x-developer-application-key': self._developer_key
        }


class BBSessionProduction(BBSession):
    _host = 'bb.com.br'


class BBClient:
    session = None

    def __init__(self, session):
        self.session = session

    @classmethod
    def from_credentials(cls, client_id, client_secret, developer_key, production=False):
        session_class = BBSession
        if production:
            session_class = BBSessionProduction
        return cls(session_class(client_id, client_secret, developer_key))

    def request(self, method, path='', params=None, data=None, *args, **kwargs):
        resp = self.session.request(method, path=path, params=params, data=data, *args, **kwargs)
        resp.raise_for_status()
        return resp

    def get_pix_recebidos(self, dthr_ini, dthr_fim):

        data = {
            'inicio': dthr_ini,
            'fim': dthr_fim
        }

        rspnc = self.request('get', data=data)

        return rspnc


if __name__ == '__main__':
    client_id = "eyJpZCI6ImFmYjk5MDktNTQyZC00ZWNmLThlOSIsImNvZGlnb1B1YmxpY2Fkb3IiOjAsImNvZGlnb1NvZnR3YXJlIjoyODM2OSwic2VxdWVuY2lhbEluc3RhbGFjYW8iOjF9x"
    client_secret = "eyJpZCI6IjA3ZDIzOTgtNGYzYi00MTgzLWFmOTMtNWZjZTUxN2YiLCJjb2RpZ29QdWJsaWNhZG9yIjowLCJjb2RpZ29Tb2Z0d2FyZSI6MjgzNjksInNlcXVlbmNpYWxJbnN0YWxhY2FvIjoxLCJzZXF1ZW5jaWFsQ3JlZGVuY2lhbCI6MSwiYW1iaWVudGUiOiJob21vbG9nYWNhbyIsImlhdCI6MTY0MjY5OTA1MDU5OH0"
    developer_key = "d27b377908ffab00136be17d60050656b9a1a5b8"
    OAUTH_ENDPOINT = "https://oauth.sandbox.bb.com.br/oauth/token"
    api_url = f"https://api.sandbox.bb.com.br/pix/v1/"

    auth = BBAuthSandbox(client_id, client_secret, developer_key)

    data = {
        'grant_type': 'client_credentials',
        'code': developer_key,
    }

    resp = requests.get(api_url, data=data, verify=False, auth=auth)
    pprint(resp.content)
    print('fim')

# resp = client.get_pix_recebidos('2021-12-20T00:00:01Z', "2021-12-24T23:59:59Z")
# {"statusCode":401,"error":"Unauthorized","message":"Bad Credentials","attributes":{"error":"Bad Credentials"}}


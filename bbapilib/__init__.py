
import requests
from requests.auth import AuthBase


class BadCredentials(Exception):
    ...


class BBAuth(AuthBase):
    OAUTH_ENDPOINT = "https://oauth.bb.com.br/oauth/token"
    USE_CERT = True

    def __init__(self, client_id, client_secret, developer_key):
        self.credentials = (client_id, client_secret)
        self.developer_key = developer_key
        self._token = None

    @property
    def token(self):
        if not self._token:
            self.renew()
        return self._token

    @token.setter
    def token(self, token):
        type_, value = token
        self._token = f'{type_} {value}x'

    def renew(self):
        data = {
            'grant_type': 'client_credentials',
            'code': self.developer_key,
        }

        resp = requests.post(self.OAUTH_ENDPOINT, data=data, verify=self.USE_CERT, auth=self.credentials)
        if resp.status_code == 401:
            raise BadCredentials()

        json = resp.json()

        self.token = json['token_type'], json['access_token']

    def __call__(self, r):
        r.headers['Authorization'] = self.token
        r.headers['x-developer-application-key'] = self.developer_key
        return r


class BBAuthSandbox(BBAuth):
    OAUTH_ENDPOINT = "https://oauth.sandbox.bb.com.br/oauth/token"
    USE_CERT = False

class BBSession(requests.Session):
    ENDPOINT = "https://api.bb.com/pix/v1/"
    USE_CERT = True

    def __init__(self, auth):
        super().__init__()
        self.auth = auth

    def request(self, method: str, path='', *args, **kwargs):
        url = self.ENDPOINT + path
        resp = super().request(method, url, *args, verify=self.USE_CERT, **kwargs)
        return resp


class BBSessionSandbox(BBSession):
    ENDPOINT = "https://api.sandbox.bb.com.br/pix/v1/"
    USE_CERT = False


class BBClient:
    AUTH = BBAuth
    SESSION = BBSession

    def __init__(self, session):
        self.session = session

    @classmethod
    def from_credentials(cls, client_id, client_secret, developer_key):
        auth = cls.AUTH(client_id, client_secret, developer_key)
        session = cls.SESSION(auth)
        return cls(session)

    def request(self, method, path='', params=None, data=None, *args, **kwargs):
        resp = self.session.request(method, path=path, params=params, data=data, *args, **kwargs)
        resp.raise_for_status()
        return resp

    def received_pixs(self, init_datetime, end_datetime):
        params = {
            'inicio': init_datetime,
            'fim': end_datetime
        }

        resp = self.request('get', params=params)

        return resp


class BBClientSandbox(BBClient):
    AUTH = BBAuthSandbox
    SESSION = BBSessionSandbox


if __name__ == '__main__':
    client_id = "eyJpZCI6ImFmYjk5MDktNTQyZC00ZWNmLThlOSIsImNvZGlnb1B1YmxpY2Fkb3IiOjAsImNvZGlnb1NvZnR3YXJlIjoyODM2OSwic2VxdWVuY2lhbEluc3RhbGFjYW8iOjF9"
    client_secret = "eyJpZCI6IjA3ZDIzOTgtNGYzYi00MTgzLWFmOTMtNWZjZTUxN2YiLCJjb2RpZ29QdWJsaWNhZG9yIjowLCJjb2RpZ29Tb2Z0d2FyZSI6MjgzNjksInNlcXVlbmNpYWxJbnN0YWxhY2FvIjoxLCJzZXF1ZW5jaWFsQ3JlZGVuY2lhbCI6MSwiYW1iaWVudGUiOiJob21vbG9nYWNhbyIsImlhdCI6MTY0MjY5OTA1MDU5OH0"
    developer_key = "d27b377908ffab00136be17d60050656b9a1a5b8"

    client = BBClientSandbox.from_credentials(
        client_id=client_id,
        client_secret=client_secret,
        developer_key=developer_key,
    )

    resp = client.received_pixs('2021-12-20T00:00:01Z', "2021-12-24T23:59:59Z")
    
    print(resp.json())

# {"statusCode":401,"error":"Unauthorized","message":"Bad Credentials","attributes":{"error":"Bad Credentials"}}


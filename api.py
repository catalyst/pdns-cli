from requests import Session
from requests.auth import AuthBase
from urllib.parse import urljoin

import models


class APIKeyAuth(AuthBase):

    def __init__(self, api_key):
        self.api_key = api_key

    def __call__(self, r):
        r.headers['X-API-Key'] = self.api_key
        return r


class BaseURLSession(Session):

    base_url = None

    def __init__(self, base_url=None):
        if base_url:
            self.base_url = base_url
        super().__init__()

    def request(self, method, url, *args, **kwargs):
        url = self.create_url(url)
        return super().request(method, url, *args, **kwargs)

    def create_url(self, url):
        return urljoin(self.base_url, url)


class PDNSAPI(object):

    def __init__(self, url, api_key=None, basic_auth=None, verify=True):
        self.session = BaseURLSession(url)
        self.session.verify = verify
        self.session.headers.update({'Accept': 'application/json'})

        if api_key:
            self.session.auth = APIKeyAuth(api_key)
        elif basic_auth:
            self.session.auth = basic_auth

    def get(self, url, *args, **kwargs):
        r = self.session.get(url, *args, **kwargs)
        r.raise_for_status()
        return r

    def post(self, url, *args, **kwargs):
        r = self.session.post(url, *args, **kwargs)
        r.raise_for_status()
        return r

    def put(self, url, *args, **kwargs):
        r = self.session.put(url, *args, **kwargs)
        r.raise_for_status()
        return r

    def patch(self, url, *args, **kwargs):
        r = self.session.patch(url, *args, **kwargs)
        r.raise_for_status()
        return r

    def delete(self, url, *args, **kwargs):
        r = self.session.delete(url, *args, **kwargs)
        r.raise_for_status()
        return r

    @property
    def servers(self):
        return models.Server.all(self)

    def server(self, name):
        return models.Server(self, name)

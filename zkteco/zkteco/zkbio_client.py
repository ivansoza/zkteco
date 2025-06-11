import requests
from urllib.parse import urljoin
from django.conf import settings

class ZKBioClient:
    """Simple client for ZKBio CVSecurity API."""

    def __init__(self):
        self.base_url = settings.BASE_URL.rstrip('/')
        self.client_id = settings.CLIENT_ID
        self.client_secret = settings.CLIENT_SECRET
        self._access_token = None

    def get_access_token(self):
        """Retrieve and cache an access token."""
        url = urljoin(self.base_url + '/', 'api/auth/token')
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            self._access_token = response.json().get('access_token')
        except requests.RequestException as exc:
            raise RuntimeError('Unable to obtain access token') from exc
        return self._access_token

    def _get_headers(self, headers=None):
        headers = headers.copy() if headers else {}
        if not self._access_token:
            self.get_access_token()
        headers.setdefault('Authorization', f'Bearer {self._access_token}')
        return headers

    def get(self, path, **kwargs):
        """Send a GET request with authorization."""
        url = urljoin(self.base_url + '/', path.lstrip('/'))
        headers = self._get_headers(kwargs.pop('headers', None))
        response = requests.get(url, headers=headers, **kwargs)
        response.raise_for_status()
        return response

    def post(self, path, data=None, json=None, **kwargs):
        """Send a POST request with authorization."""
        url = urljoin(self.base_url + '/', path.lstrip('/'))
        headers = self._get_headers(kwargs.pop('headers', None))
        response = requests.post(url, headers=headers, data=data, json=json, **kwargs)
        response.raise_for_status()
        return response

# Example usage:
# from zkteco.zkbio_client import ZKBioClient
# client = ZKBioClient()
# token = client.get_access_token()  # Optional: token retrieved lazily otherwise
# response = client.get('/api/some/endpoint')
# print(response.json())

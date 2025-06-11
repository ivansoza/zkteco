import requests
from urllib.parse import urljoin
from django.conf import settings
class ZKBioClient:
    """ZKBio client using static token in URL parameters."""

    def __init__(self):
        api_conf = getattr(settings, "ZKBIO_API", {})
        self.base_url = api_conf.get("BASE_URL", "").rstrip("/")
        self.access_token = api_conf.get("ACCESS_TOKEN")

    def post(self, path, params=None):
        """POST request using token in query params."""
        if params is None:
            params = {}
        params["access_token"] = self.access_token

        url = urljoin(self.base_url + '/', path.lstrip('/'))

        try:
            response = requests.post(url, params=params, verify=False)
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            raise RuntimeError(f"API call failed: {exc}")

    def get(self, path, params=None):
        """GET request using token in query params."""
        if params is None:
            params = {}
        params["access_token"] = self.access_token

        url = urljoin(self.base_url + '/', path.lstrip('/'))

        try:
            response = requests.get(url, params=params, verify=False)
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            raise RuntimeError(f"API call failed: {exc}")

# Example usage:
# from zkteco.zkbio_client import ZKBioClient
# client = ZKBioClient()
# token = client.get_access_token()  # Optional: token retrieved lazily otherwise
# response = client.get('/api/some/endpoint')
# print(response.json())

import requests
from urllib.parse import urljoin
from django.conf import settings
class ZKBioClient:
    """ZKBio client using static token in URL parameters only."""

    def __init__(self):
        api_conf = getattr(settings, "ZKBIO_API", {})
        self.base_url = api_conf.get("BASE_URL", "").rstrip("/")
        self.access_token = api_conf.get("ACCESS_TOKEN")

    def post(self, path, data=None):
        """POST with token in query param and data in form-encoded body."""
        url = urljoin(self.base_url + '/', path.lstrip('/'))
        params = {"access_token": self.access_token}
        try:
            response = requests.post(url, params=params, data=data, verify=False)
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

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
            response = requests.post(url, params=params, data=data, verify=False)  # verify=False aquí
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            raise RuntimeError(f"API POST call failed: {exc}")

    def get(self, path, params=None):
        """GET request using token in query params."""
        if params is None:
            params = {}
        params["access_token"] = self.access_token

        url = urljoin(self.base_url + '/', path.lstrip('/'))
        try:
            response = requests.get(url, params=params, verify=False)  # verify=False aquí también
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            raise RuntimeError(f"API GET call failed: {exc}")

    def get_person_list(self, pins="", dept_codes="", page_no=1, page_size=100):
        """Return paginated personnel list using the getPersonList endpoint."""
        data = {
            "pins": pins,
            "deptCodes": dept_codes,
            "pageNo": page_no,
            "pageSize": page_size,
        }
        return self.post("api/v2/person/getPersonList", data=data)

    def get_transactions(
        self,
        person_pin="",
        start_date="",
        end_date="",
        page_no=1,
        page_size=1000,
        gate_only=False,
        v2=True,
    ):
        """Return paginated access transactions.

        Parameters mirror the API query parameters. If ``gate_only`` is
        ``True`` the gate transaction endpoint is used. ``v2`` selects the
        version of the endpoint.
        """

        base = "psgTransaction/list" if gate_only else "transaction/list"
        path = f"api/{'v2/' if v2 else ''}{base}"

        params = {
            "personPin": person_pin,
            "startDate": start_date,
            "endDate": end_date,
            "pageNo": page_no,
            "pageSize": page_size,
        }

        return self.get(path, params=params)

# Example usage:
# from zkteco.zkbio_client import ZKBioClient
# client = ZKBioClient()
# token = client.get_access_token()  # Optional: token retrieved lazily otherwise
# response = client.get('/api/some/endpoint')
# print(response.json())

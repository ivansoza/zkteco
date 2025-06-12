import requests
from urllib.parse import urljoin
from django.conf import settings
class ZKBioClient:
    """Cliente ZKBio que usa token estático en query‐string."""

    def __init__(self):
        api_conf        = getattr(settings, "ZKBIO_API", {})
        self.base_url   = api_conf.get("BASE_URL", "").rstrip("/")
        self.access_tok = api_conf.get("ACCESS_TOKEN")

    # ------------------------------------------------------------------
    # Helpers HTTP
    # ------------------------------------------------------------------

    def _post(self, path: str, body: dict | None = None):
        """POST → siempre JSON + token en la URL."""
        url    = urljoin(self.base_url + "/", path.lstrip("/"))
        params = {"access_token": self.access_tok}

        try:
            resp = requests.post(
                url,
                params=params,
                json=body or {},                # 👈 cuerpo JSON
                headers={"Content-Type": "application/json"},
                verify=False,                   # self-signed cert
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            raise RuntimeError(f"API POST call failed: {exc}")

    def _get(self, path: str, params: dict | None = None):
        """GET con token en la URL."""
        params = (params or {}) | {"access_token": self.access_tok}
        url    = urljoin(self.base_url + "/", path.lstrip("/"))

        try:
            resp = requests.get(url, params=params, verify=False, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            raise RuntimeError(f"API GET call failed: {exc}")

    # ------------------------------------------------------------------
    # Personas
    # ------------------------------------------------------------------

    def get_person_list(self, pins: str = "", dept_codes: str = "",
                        page_no: int = 1, page_size: int = 100):
        """Lista paginada de personal."""
        body = {
            "pins": pins,
            "deptCodes": dept_codes,
            "pageNo": page_no,
            "pageSize": page_size,
        }
        return self._post("api/v2/person/getPersonList", body)

    def update_person_photo(self, pin: int, person_photo_b64: str):
        """Actualiza la foto (Base64) de la persona."""
        body = {"pin": str(pin), "personPhoto": person_photo_b64}
        return self._post("api/person/updatePersonnelPhoto", body)

    def delete_person(self, pin: int):
        """
        Confirmado por Postman:
        POST /api/person/delete/{pin}?access_token=TOKEN
        (acepta token vía query‐string y sin body)
        """
        url = urljoin(self.base_url + "/", f"api/person/delete/{pin}")
        resp = requests.post(
            url,
            params={"access_token": self.access_tok},
            verify=False,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # Transacciones
    # ------------------------------------------------------------------

    def get_transactions(
        self,
        person_pin: str = "",
        start_date: str = "",
        end_date: str = "",
        page_no: int = 1,
        page_size: int = 1000,
        gate_only: bool = False,
        v2: bool = True,
    ):
        """Accesos / transacciones."""
        base  = "psgTransaction/list" if gate_only else "transaction/list"
        path  = f"api/{'v2/' if v2 else ''}{base}"
        query = {
            "personPin": person_pin,
            "startDate": start_date,
            "endDate": end_date,
            "pageNo": page_no,
            "pageSize": page_size,
        }
        return self._get(path, query)

    # ------------------------------------------------------------------
    # Dispositivos
    # ------------------------------------------------------------------

    def get_device_list(self, module: str = "acc",
                        page_no: int = 1, page_size: int = 100, v2: bool = True):
        """Lista paginada de dispositivos del módulo indicado."""
        if module == "acc":
            path = f"api/{'v2/' if v2 else ''}device/{'list' if v2 else 'accList'}"
        elif module == "psg":
            path = f"api/{'v2/' if v2 else ''}psgDevice/list"
        elif module == "ele":
            path = "api/eleDevice/eleList"
        elif module == "ins":
            path = "api/device/attAdDeviceList"
        else:
            raise ValueError(f"Unknown module: {module}")

        return self._get(path, {"pageNo": page_no, "pageSize": page_size})

    def get_device_info(self, module: str, sn: str):
        """Info de un dispositivo vía serial number."""
        if module == "acc":
            path = "api/device/getAcc"
        elif module == "psg":
            path = "api/psgDevice/getBySn"
        else:
            raise ValueError(f"Info endpoint not defined for module: {module}")

        return self._get(path, {"sn": sn})
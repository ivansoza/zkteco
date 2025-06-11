from django.shortcuts import render
from .zkbio_client import ZKBioClient
import base64
from datetime import datetime


def home(request):
    return render(request, "home.html")


def validate_datetime(value):
    try:
        datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        return True
    except ValueError:
        return False

def is_base64(s):
    try:
        return base64.b64encode(base64.b64decode(s)).decode('utf-8') == s
    except Exception:
        return False

def add_person(request):
    result = None
    error = None

    if request.method == "POST":
        try:
            client = ZKBioClient()     
            data = {
                "pin": request.POST.get("pin"),
                "name": request.POST.get("name"),
                "deptCode": request.POST.get("deptCode"),
                "gender": request.POST.get("gender", "M"),
                "personPwd": request.POST.get("personPwd", "123456"),
                "cardNo": request.POST.get("cardNo", "000000"),
                "certNumber": request.POST.get("certNumber", "000000"),
                "certType": request.POST.get("certType", "2"),
                "accLevelIds": request.POST.get("accLevelIds", "1"),
                "accStartTime": request.POST.get("accStartTime", "2024-06-10 00:00:00"),
                "accEndTime": request.POST.get("accEndTime", "2025-06-10 23:59:59"),
                "personPhoto": request.POST.get("personPhoto", "")
            }

            # Filtrar vacíos
            data = {k: v for k, v in data.items() if v}
            result = client.post("api/person/add", data=data)

        except Exception as exc:
            error = str(exc)

    return render(request, "add_person.html", {"result": result, "error": error})


def delete_person_level(request):
    """Call the Delete Person Level API and display the result."""
    result = None
    error = None
    if request.method == "POST":
        pin = request.POST.get("pin")
        level_ids = request.POST.get("level_ids")
        if not pin or not level_ids:
            error = "Both pin and level IDs are required"
        else:
            client = ZKBioClient()
            try:
                response = client.post(
                    "api/accLevel/deleteLevel",
                    params={"pin": pin, "levelIds": level_ids},
                )
                result = response.json()
            except Exception as exc:
                error = str(exc)
    return render(
        request,
        "delete_person_level.html",
        {"result": result, "error": error},
    )


def get_qr_code(request):
    """Call the Get QR Code API and display the QR as an image."""
    result = None
    qr_base64 = None
    error = None

def get_person(request):
    """Retrieve person info by pin and display the result."""
    result = None
    error = None

    if request.method == "POST":
        pin = request.POST.get("pin", "").strip()
        if not pin:
            error = "pin is required"
        else:
            client = ZKBioClient()
            try:
                api_path = f"api/person/getQrCode/{pin}"
                result = client.post(api_path, params={"pin": pin})
                if isinstance(result, dict) and result.get("code") == 0:
                    qr_base64 = result.get("data")
            except Exception as exc:
                error = str(exc)

    return render(
        request,
        "get_qr_code.html",
        {"result": result, "qr_base64": qr_base64, "error": error},
    )
                result = client.get(f"api/person/get/{pin}")
            except Exception as exc:
                error = str(exc)

    return render(request, "get_person.html", {"result": result, "error": error})

from django.shortcuts import render
from .zkbio_client import ZKBioClient
import base64
from datetime import datetime
import io
import base64
import qrcode

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

    if request.method == "POST":
        pin = request.POST.get("pin", "").strip()
        if not pin:
            error = "El PIN es obligatorio."
        else:
            client = ZKBioClient()
            try:
                # Llamas al endpoint, que te devuelve el texto a codificar
                result = client.post(f"api/person/getQrCode/{pin}", data={"pin": pin})
                if result.get("code") == 0:
                    qr_data = result.get("data")  # ej. "2#Ct4PZoND9X/5g/…"
                    
                    # Genera el QR
                    img = qrcode.make(qr_data)
                    buffer = io.BytesIO()
                    img.save(buffer, format="PNG")
                    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
                else:
                    error = result.get("message", "No se pudo obtener el código QR.")
            except Exception as exc:
                error = str(exc)

    return render(request, "get_qr_code.html", {
        "result": result,
        "qr_base64": qr_base64,
        "error": error,
    })

def get_person(request):
    """Retrieve person info by pin and display the result."""
    result = None
    error = None

    if request.method == "POST":
        pin = request.POST.get("pin", "").strip()
        if not pin:
            error = "El PIN es obligatorio."
        else:
            client = ZKBioClient()
            try:
                response = client.get(f"api/person/get/{pin}")
                if isinstance(response, dict) and response.get("code") == 0:
                    result = response
                elif isinstance(response, dict):
                    error = response.get("message", "No se pudo obtener la información")
                else:
                    result = response
            except Exception as exc:
                error = str(exc)

    return render(request, "get_person.html", {
        "result": result,
        "error": error,
    })


def list_personnel(request):
    """Retrieve a paginated list of personnel from the ZKBio API."""
    result = None
    error = None

    if request.method == "POST":
        pins = request.POST.get("pins", "")
        dept_codes = request.POST.get("deptCodes", "")
        try:
            page_no = int(request.POST.get("pageNo", 1))
        except (TypeError, ValueError):
            page_no = 1
        try:
            page_size = int(request.POST.get("pageSize", 100))
        except (TypeError, ValueError):
            page_size = 100

        client = ZKBioClient()
        try:
            result = client.get_person_list(
                pins=pins,
                dept_codes=dept_codes,
                page_no=page_no,
                page_size=page_size,
            )
        except Exception as exc:
            error = str(exc)

    return render(request, "list_personnel.html", {
        "result": result,
        "error": error,
    })
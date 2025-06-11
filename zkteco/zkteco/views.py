from django.shortcuts import render
from .zkbio_client import ZKBioClient
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import base64
from datetime import datetime
import io
import base64
import qrcode
from django.views.decorators.http import require_http_methods
from django.conf import settings

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
    """Render the personnel list page."""

    return render(request, "list_personnel.html")


@require_http_methods(["GET"])
def list_personnel_data(request):
    """Return personnel data in the format expected by DataTables."""

    try:
        draw = int(request.GET.get("draw", 1))
    except (TypeError, ValueError):
        draw = 1

    try:
        start = int(request.GET.get("start", 0))
    except (TypeError, ValueError):
        start = 0

    try:
        length = int(request.GET.get("length", 10))
    except (TypeError, ValueError):
        length = 10

    pins = request.GET.get("pins", "")
    dept_codes = request.GET.get("deptCodes", "")

    page_no = start // length + 1
    page_size = length

    client = ZKBioClient()
    try:
        payload = client.get_person_list(
            pins=pins,
            dept_codes=dept_codes,
            page_no=page_no,
            page_size=page_size,
        )
        data = payload.get("data", {}) if isinstance(payload, dict) else {}
        records = data.get("data", [])
        total = data.get("total", 0)

        return JsonResponse(
            {
                "draw": draw,
                "recordsTotal": total,
                "recordsFiltered": total,
                "data": records,
            }
        )
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)

def list_transactions(request):
    """Retrieve access transactions using the ZKBio API."""
    result = None
    error = None

    if request.method == "POST":
        person_pin = request.POST.get("personPin", "")
        start_date = request.POST.get("startDate", "")
        end_date = request.POST.get("endDate", "")
        try:
            page_no = int(request.POST.get("pageNo", 1))
        except (TypeError, ValueError):
            page_no = 1
        try:
            page_size = int(request.POST.get("pageSize", 1000))
        except (TypeError, ValueError):
            page_size = 1000

        gate_only = request.POST.get("gateOnly") == "on"
        v2 = request.POST.get("version", "v2") == "v2"

        client = ZKBioClient()
        try:
            result = client.get_transactions(
                person_pin=person_pin,
                start_date=start_date,
                end_date=end_date,
                page_no=page_no,
                page_size=page_size,
                gate_only=gate_only,
                v2=v2,
            )
        except Exception as exc:
            error = str(exc)

    return render(request, "list_transactions.html", {
        "result": result,
        "error": error,
    })


def list_devices(request):
    """List devices for a selected module using the ZKBio API."""

    result = None
    error = None
    module = "acc"

    if request.method == "POST":
        module = request.POST.get("module", "acc") or "acc"
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
            result = client.get_device_list(
                module=module,
                page_no=page_no,
                page_size=page_size,
            )
        except Exception as exc:
            error = str(exc)

    return render(
        request,
        "list_devices.html",
        {"result": result, "error": error, "module": module},
    )


def device_detail(request):
    """Retrieve information for a specific device by module and serial number."""

    result = None
    error = None
    module = request.GET.get("module", "acc")
    sn = request.GET.get("sn", "")

    if sn:
        client = ZKBioClient()
        try:
            result = client.get_device_info(module, sn)
        except Exception as exc:
            error = str(exc)
    else:
        error = "SN no proporcionado"

    return render(
        request,
        "device_detail.html",
        {"result": result, "error": error, "module": module, "sn": sn},
    )


@require_http_methods(["DELETE"])              # el front-end sigue enviando DELETE
def delete_person(request, pin):
    payload = ZKBioClient().delete_person(pin) # ← hará POST al panel

    if isinstance(payload, dict) and payload.get("code") == 0:
        return JsonResponse({"success": True})

    return JsonResponse(
        {
            "success": False,
            "message": payload.get("message", "No se pudo eliminar")
        },
        status=400
    )
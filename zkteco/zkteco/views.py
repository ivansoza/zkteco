from django.shortcuts import render
from .zkbio_client import ZKBioClient


def home(request):
    return render(request, "home.html")


def add_person(request):
    """Call the Add Person API and display the result."""
    result = None
    error = None
    if request.method == "POST":
        params = {
            "pin": request.POST.get("pin", "").strip(),
            "deptCode": request.POST.get("deptCode", "").strip(),
            "name": request.POST.get("name", "").strip(),
            "lastName": request.POST.get("lastName", "").strip(),
            "gender": request.POST.get("gender", "").strip(),
            "cardNo": request.POST.get("cardNo", "").strip(),
            "personPhoto": request.POST.get("personPhoto", "").strip(),
            "accLevelIds": request.POST.get("accLevelIds", "").strip(),
            "accStartTime": request.POST.get("accStartTime", "").strip(),
            "accEndTime": request.POST.get("accEndTime", "").strip(),
        }

        if not params["pin"] or not params["deptCode"] or not params["name"]:
            error = "pin, deptCode and name are required"
        else:
            client = ZKBioClient()
            try:
                result = client.post("api/person/add", params=params)
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
                result = client.get(f"api/person/get/{pin}")
            except Exception as exc:
                error = str(exc)

    return render(request, "get_person.html", {"result": result, "error": error})

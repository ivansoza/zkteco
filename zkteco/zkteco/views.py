from django.shortcuts import render
from .zkbio_client import ZKBioClient


def home(request):
    """Render the home page with links to available tests."""
    return render(request, "home.html")


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

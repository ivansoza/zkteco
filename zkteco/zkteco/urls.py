"""URL configuration for zkteco project."""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("add_person/", views.add_person, name="add_person"),
    path("delete_person_level/", views.delete_person_level, name="delete_person_level"),
    path("get_qr_code/", views.get_qr_code, name="get_qr_code"),
    path("get_person/", views.get_person, name="get_person"),
    path("list_personnel/", views.list_personnel, name="list_personnel"),
    path("list_transactions/", views.list_transactions, name="list_transactions"),
    path("list_devices/", views.list_devices, name="list_devices"),
    path("device_detail/", views.device_detail, name="device_detail"),
    # urls.py
    path(
        "person/delete/<int:pin>/",
        views.delete_person,
        name="delete_person"
    ),
    path("admin/", admin.site.urls),
]

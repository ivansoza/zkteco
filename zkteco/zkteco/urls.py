"""URL configuration for zkteco project."""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("delete_person_level/", views.delete_person_level, name="delete_person_level"),
    path("admin/", admin.site.urls),
]

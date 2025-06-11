"""URL configuration for zkteco project."""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("add_person/", views.add_person, name="add_person"),
    path("delete_person_level/", views.delete_person_level, name="delete_person_level"),
    path("admin/", admin.site.urls),
]

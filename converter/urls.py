from django.urls import path

from . import views

app_name = "converter"

urlpatterns = [
    path("", views.index, name="index"),
    path("preview/", views.preview, name="preview"),
    path("upload/", views.upload, name="upload"),
]

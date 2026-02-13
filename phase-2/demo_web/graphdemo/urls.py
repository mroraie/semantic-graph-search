from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("llm_status/", views.llm_status, name="llm_status"),
]



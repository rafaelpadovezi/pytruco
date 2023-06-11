from django.urls import include, path

from pytruco.apps.core.api.v1 import views

urlpatterns = [
    path("v1/game", views.GameView.as_view()),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]

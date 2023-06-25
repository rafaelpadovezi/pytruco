from django.urls import include, path

from pytruco.apps.core.api.v1 import views

urlpatterns = [
    path("v1/game/", views.GameView.as_view()),
    path("v1/game/<int:id>/", views.GameView.as_view()),
    path("v1/game/<int:player_id>/cards", views.cards),
    path("v1/game/<int:player_id>/play", views.play),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]

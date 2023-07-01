from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from pytruco.apps.core.api.v1 import views

urlpatterns = [
    path("v1/game/", views.CreateGameView.as_view()),
    path("v1/game/<int:id>/", views.get_game_state),
    path("v1/game/<int:player_id>/cards", views.cards),
    path("v1/game/<int:player_id>/play", views.play),
    # DRF spectacular
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]

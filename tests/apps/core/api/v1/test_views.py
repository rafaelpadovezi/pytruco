from django.test import Client, TestCase

from pytruco.apps.core.models import Game


class GameViewTest(TestCase):
    def test_should_create_a_new_game(self):
        client = Client()

        response = client.post("/v1/game")

        # assert
        self.assertEqual(response.status_code, 200)
        db_game = Game.objects.all()[0]
        self.assertEqual(
            response.json(),
            {
                "game": db_game.id,
                "player1": db_game.player1.id,
                "player2": db_game.player2.id,
            },
        )

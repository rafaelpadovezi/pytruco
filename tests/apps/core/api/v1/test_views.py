from django.test import Client, TestCase

from pytruco.apps.core.models import Game, Hand, PlayerCard


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
        self.assertEqual(db_game.round_set.count(), 1)
        db_round = db_game.round_set.all()[0]
        self.assertEqual(db_round.is_current, True)
        self.assertEqual(db_round.who_starts, 1)
        self.assertEqual(db_round.number, 1)
        self.assertEqual(db_round.points_in_game, 1)
        self.assertEqual(db_round.points_being_raised, 1)

        self.assertEqual(db_round.hand_set.count(), 1)
        db_hand = db_round.hand_set.all()[0]
        self.assertEqual(db_hand.is_current, True)
        self.assertEqual(db_hand.number, 1)
        self.assertEqual(db_hand.result, Hand.HandResult.Playing)

        player1_cards = PlayerCard.objects.filter(
            round__id=db_round.id, player__id=db_game.player1.id
        )
        self.assertEqual(player1_cards.count(), 3)
        player2_cards = PlayerCard.objects.filter(
            round__id=db_round.id, player__id=db_game.player2.id
        )
        self.assertEqual(player2_cards.count(), 3)

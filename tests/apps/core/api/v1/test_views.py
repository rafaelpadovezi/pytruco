from django.test import Client, TestCase

from pytruco.apps.core.models import Game, Hand, PlayerCard
from tests.utils import create_brand_new_game


class GameViewTest(TestCase):
    def test_should_create_a_new_game(self):
        client = Client()

        response = client.post("/v1/game/")

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
        self.assertEqual(db_hand.result, Hand.Result.Playing)

        player1_cards = PlayerCard.objects.filter(
            round__id=db_round.id, player__id=db_game.player1.id
        )
        self.assertEqual(player1_cards.count(), 3)
        player2_cards = PlayerCard.objects.filter(
            round__id=db_round.id, player__id=db_game.player2.id
        )
        self.assertEqual(player2_cards.count(), 3)

    def test_should_get_state_of_a_new_game(self):
        # arrange
        (game_id, _, _) = create_brand_new_game()

        client = Client()

        # act
        response = client.get(f"/v1/game/{game_id}/")

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "number": 1,
                "points": 1,
                "hands": [
                    {"number": 1, "CardPlayer1": [], "CardPlayer2": [], "result": 1}
                ],
                "pointsPlayer1": 0,
                "pointsPlayer2": 0,
                "lastAction": "Game started",
                "nextAction": "Player 1 turn",
            },
        )


class GameActionsViewTest(TestCase):
    def test_should_get_cards_from_player1(self):
        # arrange
        (_, player1_id, _) = create_brand_new_game()

        client = Client()

        # act
        response = client.get(f"/v1/game/{player1_id}/cards")

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"round": 1, "hand": 1, "onHand": ["6♥", "7♥", "2♥"], "played": []},
        )

    def test_should_get_cards_from_player2(self):
        # arrange
        (_, _, player2_id) = create_brand_new_game()

        client = Client()

        # act
        response = client.get(f"/v1/game/{player2_id}/cards")

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"round": 1, "hand": 1, "onHand": ["A♦", "5♦", "7♦"], "played": []},
        )

    def test_should_change_player_turn_when_player1_plays(self):
        # arrange
        (game_id, player1_id, _) = create_brand_new_game()

        client = Client()

        # act
        response = client.post(f"/v1/game/{player1_id}/play", {"card": "6♥"})

        # assert
        self.assertEqual(response.status_code, 200)
        db_game = Game.objects.get(id=game_id)
        self.assertEqual("Player 1 turn", db_game.last_action)
        self.assertEqual("Player 2 turn", db_game.next_action)
        played_card = PlayerCard.objects.get(
            round__id=db_game.round_set.get().id, player__id=player1_id, played=True
        )
        self.assertEqual(played_card.card, "6♥")

    def test_should_compute_hand_result_when_all_players_played(self):
        # arrange
        (game_id, player1_id, player2_id) = create_brand_new_game()

        client = Client()
        client.post(f"/v1/game/{player1_id}/play", {"card": "6♥"})

        # act
        response = client.post(f"/v1/game/{player2_id}/play", {"card": "A♦"})

        # assert
        self.assertEqual(response.status_code, 200)
        db_game = Game.objects.get(id=game_id)
        self.assertEqual("End of hand. 3", db_game.last_action)
        self.assertEqual("Player 2 turn", db_game.next_action)
        played_card = PlayerCard.objects.get(
            round__id=db_game.round_set.get().id, player__id=player2_id, played=True
        )
        self.assertEqual(played_card.card, "A♦")

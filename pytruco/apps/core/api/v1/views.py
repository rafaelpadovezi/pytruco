from django.db import transaction
from rest_framework.response import Response
from rest_framework.views import APIView

from pytruco.apps.core.business import Deck, GameState
from pytruco.apps.core.models import Game, Hand, Player, PlayerCard, Round


class GameView(APIView):
    def post(self, request):
        deck = Deck()
        deck.shuffle()

        player1 = Player(number=1)
        player2 = Player(number=2)
        game = Game(
            player1=player1,
            player2=player2,
            last_action=GameState.game_started_state,
            next_action=GameState.player_turn_state(1),
        )
        round = Round(game=game)
        hand = Hand(round=round)

        player_cards = []
        for i in range(1, 4):
            card = deck.draw()
            player_cards.append(PlayerCard(player=player1, card=str(card), round=round))

        for i in range(1, 4):
            card = deck.draw()
            player_cards.append(PlayerCard(player=player2, card=str(card), round=round))

        with transaction.atomic():
            player1.save()
            player2.save()
            game.save()
            round.save()
            hand.save()
            PlayerCard.objects.bulk_create(player_cards)

        return Response(
            {
                "game": game.id,
                "player1": player1.id,
                "player2": player2.id,
            }
        )

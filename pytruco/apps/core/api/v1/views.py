from django.db import transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from pytruco.apps.core import game_state
from pytruco.apps.core.business import Deck, GameRules
from pytruco.apps.core.models import Game, Hand, Player, PlayerCard, Round
from pytruco.apps.core.serializers import PlaySerializer


class GameView(APIView):
    def post(self, request: Request) -> Response:
        deck = Deck()
        deck.shuffle()

        player1 = Player(number=1)
        player2 = Player(number=2)
        game = Game(
            player1=player1,
            player2=player2,
            last_action=game_state.game_started_state,
            next_action=game_state.player_turn_state(1),
        )
        round = Round(game=game)
        hand = Hand(round=round)

        players_cards = GameRules.draw_player_cards_for_the_round(
            round, player1, player2
        )

        with transaction.atomic():
            player1.save()
            player2.save()
            game.save()
            round.save()
            hand.save()
            PlayerCard.objects.bulk_create(players_cards)

        return Response(
            {
                "game": game.id,
                "player1": player1.id,
                "player2": player2.id,
            }
        )

    def get(self, request: Request, id: int) -> Response:
        try:
            game: Game = Game.objects.get(id=id)
        except Game.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        round: Round = game.round_set.get(is_current=True)
        player_cards = PlayerCard.objects.filter(round__id=round.id, played=True)
        hands: list[Hand] = round.hand_set.all()
        hands_result = []
        for hand in hands:
            hands_result.append(
                {
                    "number": hand.number,
                    "CardPlayer1": [
                        x.card
                        for x in player_cards
                        if x.player.id == game.player1.id and x.hand == hand
                    ],
                    "CardPlayer2": [
                        x.card
                        for x in player_cards
                        if x.player.id == game.player2.id and x.hand == hand
                    ],
                    "result": hand.result,
                }
            )
        return Response(
            {
                "number": round.number,
                "points": round.points_in_game,
                "hands": hands_result,
                "pointsPlayer1": game.points_player1,
                "pointsPlayer2": game.points_player2,
                "lastAction": game.last_action,
                "nextAction": game.next_action,
            }
        )


@api_view(["GET"])
def cards(request: Request, player_id: int) -> Response:
    try:
        game = Game.objects.get(Q(player1__id=player_id) | Q(player2__id=player_id))
    except Game.DoesNotExist:
        return Response({}, status=status.HTTP_400_BAD_REQUEST)
    round = game.round_set.get(is_current=True)
    hand = round.hand_set.get(is_current=True)
    player_cards = PlayerCard.objects.filter(round__id=round.id, player__id=player_id)
    result = {
        "round": round.number,
        "hand": hand.number,
        "onHand": [x.card for x in player_cards if not x.played],
        "played": [x.card for x in player_cards if x.played],
    }
    return Response(result)


@api_view(["POST"])
def play(request: Request, player_id: int) -> Response:
    try:
        game = Game.objects.get(Q(player1__id=player_id) | Q(player2__id=player_id))
    except Game.DoesNotExist:
        return Response({}, status=status.HTTP_404_NOT_FOUND)
    current_round: Round = game.round_set.get(is_current=True)

    serializer = PlaySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    card_request = serializer.validated_data["card"]

    player_number = (
        game.player1.number if game.player1.id == player_id else game.player2.number
    )
    if not game_state.is_player_turn(game, player_number):
        return Response(
            {"message": "It's not player turn"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        player_card: PlayerCard = PlayerCard.objects.get(
            round__id=current_round.id,
            player__id=player_id,
            card=card_request,
            played=False,
        )
    except PlayerCard.DoesNotExist:
        return Response({"message": "Invalid card"}, status=status.HTTP_400_BAD_REQUEST)

    current_hand: Hand = current_round.hand_set.get(is_current=True)
    is_end_of_hand = current_hand.playercard_set.count() == 1
    player_card.played = True
    player_card.hand = current_hand

    if is_end_of_hand:
        current_hand.is_current = False
        if player_number == 1:
            player1_card = player_card
            player2_card: PlayerCard = current_hand.playercard_set.get(player__number=2)
        else:
            player1_card = current_hand.playercard_set.get(player__number=1)
            player2_card = player_card

        hands = current_round.hand_set.all()

        round_result, hand_result = GameRules.get_hand_and_round_result(
            player1_card.card, player2_card.card, hands
        )
        current_hand.result = hand_result

        if round_result is Round.Result.Playing:
            game_state.update_end_of_hand_state(game, current_hand.result)
            new_hand = Hand(number=current_hand.number + 1, round=current_round)
            with transaction.atomic():
                current_hand.save()
                new_hand.save()
                player_card.save()
                game.save()
        else:
            game_state.update_end_of_round_state(
                game, current_round.who_starts, round_result
            )
            current_round.is_current = False
            new_round = Round(number=current_round.number + 1, game=game)
            if round_result == Round.Result.Player1Win:
                game.points_player1 = game.points_player1 + current_round.points_in_game
            if round_result == Round.Result.Player2Win:
                game.points_player2 = game.points_player2 + current_round.points_in_game
            new_hand = Hand(round=new_round)
            players_cards = GameRules.draw_player_cards_for_the_round(
                new_round, game.player1, game.player2
            )
            with transaction.atomic():
                current_hand.save()
                current_round.save()
                new_round.save()
                new_hand.save()
                player_card.save()
                PlayerCard.objects.bulk_create(players_cards)
                game.save()
    else:
        game_state.update_next_player_turn_state(game)
        with transaction.atomic():
            player_card.save()
            game.save()

    return Response()

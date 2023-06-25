from django.db import transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from pytruco.apps.core.business import Card, Deck, GameState
from pytruco.apps.core.models import Game, Hand, Player, PlayerCard, Round
from pytruco.apps.core.serializers import PlaySerializer


def draw_player_cards_for_the_round(
    round: Round, player1: Player, player2: Player
) -> list[PlayerCard]:
    deck = Deck()
    deck.shuffle()

    players_cards = []
    for i in range(1, 4):
        card = deck.draw()
        players_cards.append(PlayerCard(player=player1, card=str(card), round=round))

    for i in range(1, 4):
        card = deck.draw()
        players_cards.append(PlayerCard(player=player2, card=str(card), round=round))
    return players_cards


class GameView(APIView):
    def post(self, request: Request) -> Response:
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

        players_cards = draw_player_cards_for_the_round(round, player1, player2)

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
    round: Round = game.round_set.get(is_current=True)

    serializer = PlaySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    card_request = serializer.validated_data["card"]

    player_number = (
        game.player1.number if game.player1.id == player_id else game.player2.number
    )
    if not GameState.is_player_turn(game, player_number):
        return Response(
            {"message": "It's not player turn"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        player_card: PlayerCard = PlayerCard.objects.get(
            round__id=round.id, player__id=player_id, card=card_request, played=False
        )
    except PlayerCard.DoesNotExist:
        return Response({"message": "Invalid card"}, status=status.HTTP_400_BAD_REQUEST)

    current_hand: Hand = round.hand_set.get(is_current=True)
    is_end_of_hand = current_hand.playercard_set.count() == 1
    player_card.played = True
    player_card.hand = current_hand

    if is_end_of_hand:
        round_result = Round.Result.Playing
        current_hand.is_current = False
        if player_number == 1:
            player1_card = player_card
            player2_card: PlayerCard = current_hand.playercard_set.get(player__number=2)
        else:
            player1_card = current_hand.playercard_set.get(player__number=1)
            player2_card = player_card

        hands = round.hand_set.all()

        if Card(player1_card.card).get_rank() > Card(player2_card.card).get_rank():
            current_hand.result = Hand.Result.Player1Win
            victory_condition = (
                hands.filter(result=Hand.Result.Player1Win).count() + 1 == 2
                or hands.get(number=1).result == Hand.Result.Draw
            )
            if victory_condition:
                round_result = Round.Result.Player1Win

        if Card(player1_card.card).get_rank() < Card(player2_card.card).get_rank():
            current_hand.result = Hand.Result.Player2Win
            victory_condition = (
                hands.filter(result=Hand.Result.Player2Win).count() + 1 == 2
                or hands.get(number=1).result == Hand.Result.Draw
            )
            if victory_condition:
                round_result = Round.Result.Player2Win

        if Card(player1_card.card).get_rank() == Card(player2_card.card).get_rank():
            current_hand.result = Hand.Result.Draw
            if hands.count() > 1:
                first_hand_result = hands.get(number=1).result
                if first_hand_result is Hand.Result.Player1Win:
                    round_result = Round.Result.Player1Win
                elif first_hand_result is Hand.Result.Player2Win:
                    round_result = Round.Result.Player1Win
                else:
                    raise Exception("Not implemented yet!")

        if round_result is Round.Result.Playing:
            game.last_action = GameState.end_of_hand_state(current_hand.result)
            if current_hand.result is Hand.Result.Player1Win:
                game.next_action = GameState.player_turn_state(1)
            else:
                game.next_action = GameState.player_turn_state(2)
            new_hand = Hand(number=current_hand.number + 1, round=round)
            with transaction.atomic():
                current_hand.save()
                new_hand.save()
                player_card.save()
                game.save()
        else:
            game.last_action = GameState.end_of_round_state(round_result)
            game.next_action = (
                GameState.player_turn_state(2)
                if round.who_starts == 1
                else GameState.player_turn_state(1)
            )
            round.is_current = False
            new_round = Round(number=round.number + 1, game=game)
            if round_result == Round.Result.Player1Win:
                game.points_player1 = game.points_player1 + round.points_in_game
            if round_result == Round.Result.Player2Win:
                game.points_player2 = game.points_player2 + round.points_in_game
            new_hand = Hand(round=new_round)
            players_cards = draw_player_cards_for_the_round(
                new_round, game.player1, game.player2
            )
            with transaction.atomic():
                current_hand.save()
                round.save()
                new_round.save()
                new_hand.save()
                player_card.save()
                PlayerCard.objects.bulk_create(players_cards)
                game.save()
    else:
        game.last_action = game.next_action
        if game.next_action == GameState.player_turn_state(1):
            game.next_action = GameState.player_turn_state(2)
        elif game.next_action == GameState.player_turn_state(2):
            game.next_action = GameState.player_turn_state(1)
        with transaction.atomic():
            player_card.save()
            game.save()

    return Response()

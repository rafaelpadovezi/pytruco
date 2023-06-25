from pytruco.apps.core.business import GameState
from pytruco.apps.core.models import Game, Hand, Player, PlayerCard, Round


def create_brand_new_game():
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

    players_cards = [
        PlayerCard(card="6♥", player=player1, round=round),
        PlayerCard(card="7♥", player=player1, round=round),
        PlayerCard(card="2♥", player=player1, round=round),
        PlayerCard(card="A♦", player=player2, round=round),
        PlayerCard(card="5♦", player=player2, round=round),
        PlayerCard(card="7♦", player=player2, round=round),
    ]

    player1.save()
    player2.save()
    game.save()
    round.save()
    hand.save()
    PlayerCard.objects.bulk_create(players_cards)

    return (game.id, player1.id, player2.id)

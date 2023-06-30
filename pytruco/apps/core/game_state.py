from pytruco.apps.core.models import Game, Hand

number_of_players = 2
game_started_state = "Game started"


def raise_state(player_number: int, points: int):
    return f"Player {player_number} raised to {points}"


def response_state(player_number: int):
    return f"Player {player_number} must respond"


def truco_state(player_number: int):
    return f"Player {player_number} asked truco"


def player_turn_state(player_number: int):
    return f"Player {player_number} turn"


def accepted_state(player_number: int):
    return f"Player {player_number} accepted"


def end_of_hand_state(result: int):
    return f"End of hand. {result}"


def is_player_turn(game: Game, player_id: int) -> bool:
    if game.player1.id == player_id and game.next_action == player_turn_state(1):
        return True
    if game.player2.id == player_id and game.next_action == player_turn_state(2):
        return True
    return False


def end_of_round_state(result: int) -> str:
    return f"End of round. {result}"


def update_end_of_round_state(game: Game, who_starts: int, round_result: int):
    game.last_action = end_of_round_state(round_result)
    game.next_action = player_turn_state(2) if who_starts == 1 else player_turn_state(1)


def update_next_player_turn_state(game: Game):
    game.last_action = game.next_action
    if game.next_action == player_turn_state(1):
        game.next_action = player_turn_state(2)
    elif game.next_action == player_turn_state(2):
        game.next_action = player_turn_state(1)


def update_end_of_hand_state(game: Game, result: int):
    game.last_action = end_of_hand_state(result)
    if result is Hand.Result.Player1Win:
        game.next_action = player_turn_state(1)
    else:
        game.next_action = player_turn_state(2)

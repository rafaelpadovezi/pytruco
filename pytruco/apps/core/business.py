import random

from pytruco.apps.core.models import Game, Hand


class Card:
    def __init__(self, value):
        self.rank = value[0]
        self.suit = value[1]

    def __repr__(self):
        return f"{self.rank}{self.suit}"

    def get_rank(self):
        rank_dict = {
            "3": 10,
            "2": 9,
            "A": 8,
            "K": 7,
            "J": 6,
            "Q": 5,
            "7": 4,
            "6": 3,
            "5": 2,
            "4": 1,
        }
        if self.rank == "4" and self.suit == "♣":
            return 14
        elif self.rank == "7" and self.suit == "♥":
            return 13
        elif self.rank == "A" and self.suit == "♠":
            return 12
        elif self.rank == "7" and self.suit == "♦":
            return 11
        else:
            return rank_dict[self.rank]


class Deck:
    def __init__(self):
        ranks = ["A", "2", "3", "4", "5", "6", "7", "J", "Q", "K"]
        suits = ["♥", "♠", "♦", "♣"]
        self.cards = [Card(rank + suit) for suit in suits for rank in ranks]

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        return self.cards.pop()


class GameState:
    number_of_players = 2
    game_started_state = "Game started"

    @staticmethod
    def raise_state(player_number, points):
        return f"Player {player_number} raised to {points}"

    @staticmethod
    def response_state(player_number):
        return f"Player {player_number} must respond"

    @staticmethod
    def truco_state(player_number):
        return f"Player {player_number} asked truco"

    @staticmethod
    def player_turn_state(player_number):
        return f"Player {player_number} turn"

    @staticmethod
    def accepted_state(player_number):
        return f"Player {player_number} accepted"

    @staticmethod
    def end_of_hand_state(result: Hand.Result):
        return f"End of hand. {result}"

    @staticmethod
    def is_player_turn(game: Game, player_id: int) -> bool:
        if (
            game.player1.id == player_id
            and game.next_action == GameState.player_turn_state(1)
        ):
            return True
        if (
            game.player2.id == player_id
            and game.next_action == GameState.player_turn_state(2)
        ):
            return True
        return False

    @staticmethod
    def end_of_round_state(result: int) -> str:
        return f"Enf of round. {result}"

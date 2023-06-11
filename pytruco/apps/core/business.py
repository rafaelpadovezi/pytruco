import random


class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __repr__(self):
        return f"{self.rank}{self.suit}"


class Deck:
    def __init__(self):
        ranks = ["A", "2", "3", "4", "5", "6", "7", "J", "Q", "K"]
        suits = ["♥", "♠", "♦", "♣"]
        self.cards = [Card(suit, rank) for suit in suits for rank in ranks]

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

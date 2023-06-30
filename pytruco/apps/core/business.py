import random

from pytruco.apps.core.models import Hand, Player, PlayerCard, Round


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


class GameRules:
    @staticmethod
    def get_hand_and_round_result(
        player1_card: str, player2_card: str, hands
    ) -> tuple[int, int]:
        round_result = Round.Result.Playing
        if Card(player1_card).get_rank() > Card(player2_card).get_rank():
            hand_result = Hand.Result.Player1Win
            victory_condition = (
                hands.filter(result=Hand.Result.Player1Win).count() + 1 == 2
                or hands.get(number=1).result == Hand.Result.Draw
            )
            if victory_condition:
                round_result = Round.Result.Player1Win

        elif Card(player1_card).get_rank() < Card(player2_card).get_rank():
            hand_result = Hand.Result.Player2Win
            victory_condition = (
                hands.filter(result=Hand.Result.Player2Win).count() + 1 == 2
                or hands.get(number=1).result == Hand.Result.Draw
            )
            if victory_condition:
                round_result = Round.Result.Player2Win

        else:
            hand_result = Hand.Result.Draw
            if hands.count() > 1:
                first_hand_result = hands.get(number=1).result
                if first_hand_result is Hand.Result.Player1Win:
                    round_result = Round.Result.Player1Win
                elif first_hand_result is Hand.Result.Player2Win:
                    round_result = Round.Result.Player1Win
                else:
                    raise Exception("Not implemented yet!")
        return round_result, hand_result

    @staticmethod
    def draw_player_cards_for_the_round(
        round: Round, player1: Player, player2: Player
    ) -> list[PlayerCard]:
        deck = Deck()
        deck.shuffle()

        players_cards = []
        for i in range(1, 4):
            card = deck.draw()
            players_cards.append(
                PlayerCard(player=player1, card=str(card), round=round)
            )

        for i in range(1, 4):
            card = deck.draw()
            players_cards.append(
                PlayerCard(player=player2, card=str(card), round=round)
            )
        return players_cards

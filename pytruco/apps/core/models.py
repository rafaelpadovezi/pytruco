from django.db import models


class Player(models.Model):
    number = models.IntegerField()


class Game(models.Model):
    player1 = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="player1"
    )
    player2 = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="player2"
    )
    points_player1 = models.IntegerField(default=0)
    points_player2 = models.IntegerField(default=0)
    last_action = models.CharField(max_length=100)
    next_action = models.CharField(max_length=100)


class Round(models.Model):
    number = models.IntegerField()
    is_current = models.BooleanField(default=True)
    who_starts = models.IntegerField()
    points_in_game = models.IntegerField()
    points_being_raised = models.IntegerField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE)


class Hand(models.Model):
    class HandResult(models.IntegerChoices):
        Playing = 1
        Player1Win = 2
        Player2Win = 3
        Draw = 4

    number = models.IntegerField()
    is_current = models.BooleanField(default=True)
    result = models.IntegerField(choices=HandResult.choices)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)


class PlayerCard(models.Model):
    card = models.CharField(max_length=2)
    played = models.BooleanField(default=False)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    hand = models.ForeignKey(Hand, on_delete=models.CASCADE, null=True)

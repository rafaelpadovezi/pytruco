# Generated by Django 4.2.2 on 2023-06-10 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_round"),
    ]

    operations = [
        migrations.AlterField(
            model_name="game",
            name="points_player1",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="game",
            name="points_player2",
            field=models.IntegerField(default=0),
        ),
    ]

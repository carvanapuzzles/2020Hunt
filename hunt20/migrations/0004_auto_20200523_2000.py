# Generated by Django 3.0.5 on 2020-05-23 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hunt20', '0003_puzzle_in_round'),
    ]

    operations = [
        migrations.AddField(
            model_name='puzzle',
            name='puzzle_cluephrase',
            field=models.CharField(default='DNE', max_length=100),
        ),
        migrations.AddField(
            model_name='puzzle',
            name='puzzle_midpoint',
            field=models.CharField(default='DNE', max_length=100),
        ),
    ]

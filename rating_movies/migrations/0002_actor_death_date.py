# Generated by Django 4.0.3 on 2023-04-10 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rating_movies', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='actor',
            name='death_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата смерти'),
        ),
    ]

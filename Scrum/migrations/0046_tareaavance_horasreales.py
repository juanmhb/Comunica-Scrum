# Generated by Django 5.0.6 on 2024-07-06 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Scrum', '0045_alter_tareaavance_historiausuario_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tareaavance',
            name='horasReales',
            field=models.IntegerField(default=0),
        ),
    ]

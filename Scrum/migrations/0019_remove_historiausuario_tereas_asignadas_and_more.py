# Generated by Django 4.1.5 on 2023-09-21 06:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Scrum', '0018_historiausuario_tereas_asignadas'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historiausuario',
            name='tereas_asignadas',
        ),
        migrations.AddField(
            model_name='historiausuario',
            name='tereasasignadas',
            field=models.BooleanField(default=False),
        ),
    ]

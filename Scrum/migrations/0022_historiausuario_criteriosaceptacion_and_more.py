# Generated by Django 4.1.5 on 2024-02-22 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Scrum', '0021_alter_prioridadtarea_colors'),
    ]

    operations = [
        migrations.AddField(
            model_name='historiausuario',
            name='CriteriosAceptacion',
            field=models.CharField(max_length=400, null=True),
        ),
        migrations.AddField(
            model_name='historiausuario',
            name='HorasEstimadas',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='historiausuario',
            name='IdMensaje',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='historiausuario',
            name='Prioridad',
            field=models.IntegerField(null=True),
        ),
    ]

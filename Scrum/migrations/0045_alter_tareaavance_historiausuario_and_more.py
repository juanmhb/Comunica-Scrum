# Generated by Django 5.0.6 on 2024-07-06 19:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Scrum', '0044_rename_proyecto_id_tarea_proyecto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tareaavance',
            name='HistoriaUsuario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='HistoriaTareasAvance', to='Scrum.historiausuario'),
        ),
        migrations.AlterField(
            model_name='tareaavance',
            name='tarea',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tareaAvance', to='Scrum.tarea'),
        ),
    ]

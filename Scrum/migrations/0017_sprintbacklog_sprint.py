# Generated by Django 4.1.5 on 2023-09-13 18:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Scrum', '0016_alter_prioridadtarea_options_tarea_prioridad'),
    ]

    operations = [
        migrations.AddField(
            model_name='sprintbacklog',
            name='Sprint',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='SprintSprintBacklogs', to='Scrum.sprint'),
            preserve_default=False,
        ),
    ]

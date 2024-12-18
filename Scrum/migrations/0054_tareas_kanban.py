# Generated by Django 5.0.6 on 2024-07-27 19:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Scrum', '0053_alter_tareaavance_options_tareaavance_dia_1_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tareas_kanban',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('horasDedicadas', models.IntegerField()),
                ('estado', models.CharField(choices=[('Pendiente', 'Pendiente'), ('En Proceso', 'En Proceso'), ('Completada', 'Completada')], max_length=50)),
                ('tarea', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tareas_kanban', to='Scrum.tarea')),
            ],
            options={
                'ordering': ['pk'],
            },
        ),
    ]

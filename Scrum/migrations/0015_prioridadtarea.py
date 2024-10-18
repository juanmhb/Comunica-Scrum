# Generated by Django 4.1.5 on 2023-09-11 17:40

import colorfield.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Scrum', '0014_remove_tarea_horasreales'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrioridadTarea',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prioridad', models.CharField(max_length=100)),
                ('color', colorfield.fields.ColorField(default='#FF0000', image_field=None, max_length=25, samples=None)),
            ],
        ),
    ]

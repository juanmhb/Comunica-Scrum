# Generated by Django 4.1.5 on 2024-05-27 21:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Scrum', '0037_sprint_backlog'),
        ('Mensajes', '0051_dia_sprint'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dia_sprint',
            name='sprint',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Scrum.sprint'),
        ),
    ]

# Generated by Django 4.1.5 on 2024-08-20 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Scrum', '0059_alter_tarea_fechafinalplaneado_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tareaavance',
            name='dia_31',
            field=models.CharField(blank=True, default='0/1', max_length=5),
        ),
    ]

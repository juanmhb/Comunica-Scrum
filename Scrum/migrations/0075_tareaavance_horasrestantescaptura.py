# Generated by Django 4.2.7 on 2024-11-28 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Scrum', '0074_proyecto_empresa'),
    ]

    operations = [
        migrations.AddField(
            model_name='tareaavance',
            name='horasRestantesCaptura',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]

# Generated by Django 4.2.7 on 2024-10-16 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Scrum', '0066_historiausuario_numerohu'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tareaavance',
            name='fechaAvance',
            field=models.DateField(),
        ),
    ]

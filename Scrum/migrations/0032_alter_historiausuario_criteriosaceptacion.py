# Generated by Django 4.1.5 on 2024-05-14 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Scrum', '0031_tarea_empleado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historiausuario',
            name='CriteriosAceptacion',
            field=models.CharField(blank=True, choices=[('1', 'Si'), ('2', 'No')], max_length=1, null=True),
        ),
    ]

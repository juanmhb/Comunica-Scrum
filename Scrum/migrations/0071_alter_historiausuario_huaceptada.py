# Generated by Django 4.2.7 on 2024-11-08 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Scrum', '0070_historiausuario_huaceptada'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historiausuario',
            name='HUAceptada',
            field=models.CharField(blank=True, choices=[('1', 'Si'), ('2', 'No')], default='2', max_length=1, null=True),
        ),
    ]
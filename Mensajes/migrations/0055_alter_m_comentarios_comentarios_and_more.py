# Generated by Django 4.2.7 on 2024-11-08 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Mensajes', '0054_m_archivos_archivoobj'),
    ]

    operations = [
        migrations.AlterField(
            model_name='m_comentarios',
            name='Comentarios',
            field=models.CharField(max_length=400),
        ),
        migrations.AlterField(
            model_name='m_retrospectivasprint',
            name='Comentarios',
            field=models.CharField(max_length=400),
        ),
        migrations.AlterField(
            model_name='m_retrospectivasprint',
            name='OportunidadesMejora',
            field=models.CharField(max_length=400),
        ),
    ]
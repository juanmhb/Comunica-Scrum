# Generated by Django 4.1.5 on 2024-04-27 23:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Mensajes', '0043_mensajereceptor_sprint'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mensaje',
            name='Destinatario',
        ),
    ]

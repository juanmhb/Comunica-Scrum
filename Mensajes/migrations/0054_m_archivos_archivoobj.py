# Generated by Django 4.2.7 on 2024-10-23 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Mensajes', '0053_auto_20240825_0120'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_archivos',
            name='ArchivoObj',
            field=models.BinaryField(null=True),
        ),
    ]

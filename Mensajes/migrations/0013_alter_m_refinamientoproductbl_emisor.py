# Generated by Django 4.1.5 on 2024-03-15 05:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Mensajes', '0012_alter_mensaje_emisor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='m_refinamientoproductbl',
            name='Emisor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]

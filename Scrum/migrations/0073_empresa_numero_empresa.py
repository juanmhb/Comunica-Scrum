# Generated by Django 4.2.7 on 2024-11-18 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Scrum', '0072_empresa'),
    ]

    operations = [
        migrations.AddField(
            model_name='empresa',
            name='numero_empresa',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]

# Generated by Django 4.1.5 on 2024-08-20 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Scrum', '0060_alter_tareaavance_dia_31'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tareaavance',
            name='dia_31',
            field=models.CharField(blank=True, default='0/0', max_length=5),
        ),
    ]

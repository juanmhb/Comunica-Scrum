# Generated by Django 4.1.5 on 2023-08-17 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Scrum', '0005_rename_fechaelavoracio_productbacklog_fechaelavoracion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productbacklog',
            name='fechaelavoracion',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='productbacklog',
            name='ultimaactualizacion',
            field=models.DateField(blank=True, null=True),
        ),
    ]

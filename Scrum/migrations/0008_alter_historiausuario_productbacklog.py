# Generated by Django 4.1.5 on 2023-08-17 17:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Scrum', '0007_alter_productbacklog_fechaelavoracion_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historiausuario',
            name='ProductBacklog',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='BacklogHistorias', to='Scrum.productbacklog'),
        ),
    ]

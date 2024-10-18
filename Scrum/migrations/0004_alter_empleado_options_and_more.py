# Generated by Django 4.1.5 on 2023-08-07 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Scrum', '0003_alter_tarea_estatus'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='empleado',
            options={'ordering': ['pk']},
        ),
        migrations.AlterModelOptions(
            name='empleadoproyecto',
            options={'ordering': ['pk']},
        ),
        migrations.AlterModelOptions(
            name='historiausuario',
            options={'ordering': ['pk']},
        ),
        migrations.AlterModelOptions(
            name='jefeproyecto',
            options={'ordering': ['pk']},
        ),
        migrations.AlterModelOptions(
            name='productbacklog',
            options={'ordering': ['pk']},
        ),
        migrations.AlterModelOptions(
            name='progreso',
            options={'ordering': ['pk']},
        ),
        migrations.AlterModelOptions(
            name='proyecto',
            options={'ordering': ['pk']},
        ),
        migrations.AlterModelOptions(
            name='reuniondiaria',
            options={'ordering': ['pk']},
        ),
        migrations.AlterModelOptions(
            name='sprint',
            options={'ordering': ['pk']},
        ),
        migrations.AlterModelOptions(
            name='sprintbacklog',
            options={'ordering': ['pk']},
        ),
        migrations.AlterModelOptions(
            name='tarea',
            options={'ordering': ['pk']},
        ),
        migrations.AddField(
            model_name='tarea',
            name='nombre',
            field=models.CharField(default=' ', max_length=200),
            preserve_default=False,
        ),
    ]

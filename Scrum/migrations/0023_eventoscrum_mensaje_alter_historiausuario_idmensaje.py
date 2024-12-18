# Generated by Django 4.1.5 on 2024-02-22 20:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Scrum', '0022_historiausuario_criteriosaceptacion_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventoScrum',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Descripcion', models.CharField(blank=True, max_length=40, null=True)),
            ],
            options={
                'ordering': ['pk'],
            },
        ),
        migrations.CreateModel(
            name='Mensaje',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Descripcion', models.CharField(blank=True, max_length=400, null=True)),
                ('Status', models.IntegerField()),
                ('Emisor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Scrum.empleado')),
                ('EventoScrum', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Scrum.eventoscrum')),
                ('Proyecto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Scrum.proyecto')),
            ],
            options={
                'ordering': ['pk'],
            },
        ),
        migrations.AlterField(
            model_name='historiausuario',
            name='IdMensaje',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Scrum.mensaje'),
        ),
    ]

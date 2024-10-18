# Generated by Django 4.1.5 on 2024-05-15 21:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Scrum', '0035_alter_historiausuario_prioridad'),
        ('Mensajes', '0049_delete_m_reuniondiaria'),
    ]

    operations = [
        migrations.CreateModel(
            name='m_ReunionDiaria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('FechaHora', models.DateTimeField(auto_now=True)),
                ('ObstaculosPresentados', models.CharField(max_length=500)),
                ('PlanDiaSiguiente', models.CharField(max_length=500)),
                ('TrabajoRealizadoDiaAnterior', models.CharField(max_length=500)),
                ('Emisor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Scrum.empleado')),
                ('Mensaje', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Mensajes.mensaje')),
                ('Proyecto', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Scrum.proyecto')),
                ('Sprint', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Scrum.sprint')),
            ],
            options={
                'ordering': ['pk'],
            },
        ),
    ]

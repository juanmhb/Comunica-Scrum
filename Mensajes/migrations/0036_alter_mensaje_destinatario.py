# Generated by Django 4.1.5 on 2024-03-25 22:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Scrum', '0028_remove_empleado_roles_empleado_roles'),
        ('Mensajes', '0035_alter_asistenteseventosscrum_usuario'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mensaje',
            name='Destinatario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Scrum.empleado'),
        ),
    ]

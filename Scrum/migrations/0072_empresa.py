# Generated by Django 4.2.7 on 2024-11-18 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Scrum', '0071_alter_historiausuario_huaceptada'),
    ]

    operations = [
        migrations.CreateModel(
            name='Empresa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_empresa', models.CharField(max_length=200, null=True, unique=True)),
            ],
            options={
                'ordering': ['pk'],
            },
        ),
    ]

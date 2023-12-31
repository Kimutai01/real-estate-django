# Generated by Django 4.2.4 on 2023-08-29 22:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_delete_contract'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.room')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.tenant')),
            ],
        ),
    ]

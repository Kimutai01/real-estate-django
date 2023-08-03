# Generated by Django 4.2.3 on 2023-08-02 11:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_property_image_availabletime'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='check_in',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='check_out',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='room',
        ),
        migrations.AddField(
            model_name='booking',
            name='available_time',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.availabletime'),
        ),
    ]
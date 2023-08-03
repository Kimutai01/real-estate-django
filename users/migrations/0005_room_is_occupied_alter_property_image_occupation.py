# Generated by Django 4.2.3 on 2023-08-03 03:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_remove_booking_check_in_remove_booking_check_out_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='is_occupied',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='property',
            name='image',
            field=models.ImageField(blank=True, default='default.jpg', null=True, upload_to='apartments'),
        ),
        migrations.CreateModel(
            name='Occupation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.room')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.tenant')),
            ],
        ),
    ]
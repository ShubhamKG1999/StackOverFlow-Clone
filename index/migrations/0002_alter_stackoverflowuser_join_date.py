# Generated by Django 4.2 on 2023-04-06 05:37

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stackoverflowuser',
            name='join_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]

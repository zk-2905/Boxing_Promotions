# Generated by Django 3.2.23 on 2024-01-29 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('box', '0014_auto_20240129_0006'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventregistration',
            name='matched',
            field=models.BooleanField(default=False),
        ),
    ]

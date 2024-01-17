# Generated by Django 3.2.23 on 2024-01-17 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('box', '0003_boxingevent'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='draws',
            field=models.PositiveIntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='losses',
            field=models.PositiveIntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='wins',
            field=models.PositiveIntegerField(default=0, null=True),
        ),
    ]

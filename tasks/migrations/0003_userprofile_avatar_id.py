# Generated by Django 5.0.2 on 2025-03-14 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_userprofile_avatar_url_alter_userprofile_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='avatar_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]

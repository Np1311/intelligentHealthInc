# Generated by Django 4.2.3 on 2023-08-06 15:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('systemAdmin', '0005_alter_profile_status_account'),
    ]

    operations = [
        migrations.DeleteModel(
            name='account',
        ),
    ]

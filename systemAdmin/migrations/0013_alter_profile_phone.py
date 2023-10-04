# Generated by Django 4.2.3 on 2023-08-06 18:59

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('systemAdmin', '0012_alter_profile_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='phone',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=128, region='SG'),
        ),
    ]

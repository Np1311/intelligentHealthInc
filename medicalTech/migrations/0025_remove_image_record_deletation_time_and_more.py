# Generated by Django 4.2.3 on 2023-11-06 09:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('medicalTech', '0024_merge_20231106_1731'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image_record',
            name='deletation_time',
        ),
        migrations.RemoveField(
            model_name='radiologyrecord',
            name='update_time',
        ),
    ]

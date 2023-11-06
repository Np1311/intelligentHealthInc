# Generated by Django 4.2.3 on 2023-11-06 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medicalTech', '0025_remove_image_record_deletation_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='image_record',
            name='deletation_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='radiologyrecord',
            name='upload_time',
            field=models.DateTimeField(null=True),
        ),
    ]

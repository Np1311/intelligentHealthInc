# Generated by Django 4.2.3 on 2023-10-21 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medicalTech', '0020_alter_image_record_upload_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='image_record',
            name='medTech',
            field=models.CharField(max_length=255, null=True),
        ),
    ]

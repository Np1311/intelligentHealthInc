# Generated by Django 4.2.3 on 2023-10-07 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("medicalTech", "0014_alter_radiologyrecord_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="image_record",
            name="image",
            field=models.BinaryField(null=True),
        ),
    ]
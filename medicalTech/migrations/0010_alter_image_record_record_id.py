# Generated by Django 4.2.3 on 2023-09-09 03:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('medicalTech', '0009_image_record_image_filename'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image_record',
            name='record_id',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='medicalTech.radiologyrecord'),
        ),
    ]

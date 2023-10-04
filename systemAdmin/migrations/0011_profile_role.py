# Generated by Django 4.2.3 on 2023-08-06 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('systemAdmin', '0010_delete_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='role',
            field=models.CharField(choices=[('systemAdmin', 'System Admin'), ('medicalTech', 'Medical Technician'), ('healtcareAdmin', 'Healtcare Admin'), ('radiologoistDoctor', 'Radiologist Doctor')], default='active', max_length=50),
        ),
    ]

# Generated by Django 4.2.3 on 2023-08-20 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medicalTech', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='radiologyrecord',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')], default='', max_length=20),
        ),
    ]

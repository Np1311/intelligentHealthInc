# Generated by Django 4.2.3 on 2023-10-17 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='findingsTemplate',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('template_name', models.CharField(max_length=255)),
                ('template', models.TextField()),
            ],
        ),
    ]

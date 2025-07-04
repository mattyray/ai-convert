# Generated by Django 5.1.6 on 2025-06-30 19:27

import imagegen.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imagegen', '0003_alter_generatedimage_output_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='generatedimage',
            name='cleanup_attempted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='generatedimage',
            name='expires_at',
            field=models.DateTimeField(default=imagegen.models.get_expiration_time),
        ),
        migrations.AddField(
            model_name='generatedimage',
            name='is_expired',
            field=models.BooleanField(default=False),
        ),
    ]

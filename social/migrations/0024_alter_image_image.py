# Generated by Django 4.0.4 on 2022-10-29 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0023_alter_image_image_alter_messagemodel_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='uploads'),
        ),
    ]

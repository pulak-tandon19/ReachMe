# Generated by Django 4.0.4 on 2022-10-29 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0021_alter_messagemodel_receiver_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='messagemodel',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='picture',
            field=models.ImageField(blank=True, default='uploads/profile_pictures/default.png', upload_to=''),
        ),
    ]
# Generated by Django 4.0.1 on 2022-02-22 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0019_comment_comment_level'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='comment_level',
            field=models.IntegerField(),
        ),
    ]

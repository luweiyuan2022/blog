# Generated by Django 2.2.12 on 2022-02-13 11:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('topic', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='topic',
            old_name='create_time',
            new_name='created_time',
        ),
    ]
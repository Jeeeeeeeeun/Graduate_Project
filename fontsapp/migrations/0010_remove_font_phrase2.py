# Generated by Django 3.0.6 on 2020-08-23 12:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fontsapp', '0009_auto_20200814_1527'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='font',
            name='phrase2',
        ),
    ]

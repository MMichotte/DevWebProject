# Generated by Django 3.0.3 on 2020-03-08 15:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('toolbox_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='persons',
            name='email',
        ),
    ]

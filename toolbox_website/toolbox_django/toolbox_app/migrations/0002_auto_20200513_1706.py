# Generated by Django 3.0.3 on 2020-05-13 15:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('toolbox_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupsmembers',
            name='id_person',
            field=models.ForeignKey(db_column='id_person', on_delete=django.db.models.deletion.DO_NOTHING, to='toolbox_app.Persons'),
        ),
        migrations.AlterField(
            model_name='toolsgroups',
            name='id_tool',
            field=models.ForeignKey(db_column='id_tool', on_delete=django.db.models.deletion.DO_NOTHING, to='toolbox_app.Tools'),
        ),
    ]
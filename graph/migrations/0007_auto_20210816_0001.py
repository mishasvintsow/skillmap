# Generated by Django 3.2.6 on 2021-08-15 21:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('graph', '0006_auto_20210815_1040'),
    ]

    operations = [
        migrations.RenameField(
            model_name='edge',
            old_name='vertex_from',
            new_name='source',
        ),
        migrations.RenameField(
            model_name='edge',
            old_name='vertex_to',
            new_name='target',
        ),
    ]

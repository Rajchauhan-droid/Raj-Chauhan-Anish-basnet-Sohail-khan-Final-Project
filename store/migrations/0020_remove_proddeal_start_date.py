# Generated by Django 5.0.1 on 2024-05-13 02:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0019_delete_producttimer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proddeal',
            name='start_date',
        ),
    ]

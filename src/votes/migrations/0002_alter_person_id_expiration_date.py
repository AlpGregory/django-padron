# Generated by Django 4.1.7 on 2023-03-22 06:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('votes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='id_expiration_date',
            field=models.DateField(),
        ),
    ]

# Generated by Django 2.2.6 on 2021-04-28 12:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taxManagement', '0005_auto_20210428_1426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoiceheader',
            name='date_time_issued',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 28, 14, 39, 33, 907189)),
        ),
    ]

# Generated by Django 2.2.6 on 2021-03-01 08:09

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taxManagement', '0006_auto_20210301_0809'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoiceheader',
            name='date_time_issued',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2021, 3, 1, 8, 9, 34, 548451), null=True),
        ),
    ]

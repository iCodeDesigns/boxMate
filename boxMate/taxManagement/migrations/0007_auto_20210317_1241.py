# Generated by Django 2.2.6 on 2021-03-17 10:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taxManagement', '0006_auto_20210317_1237'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoiceline',
            name='currencySold',
        ),
        migrations.AlterField(
            model_name='invoiceheader',
            name='date_time_issued',
            field=models.DateTimeField(default=datetime.datetime(2021, 3, 17, 12, 41, 9, 325871)),
        ),
    ]

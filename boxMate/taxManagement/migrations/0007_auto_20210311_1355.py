# Generated by Django 2.2.6 on 2021-03-11 13:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taxManagement', '0006_auto_20210311_1355'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='maintable',
            name='currency_sold',
        ),
        migrations.AlterField(
            model_name='invoiceheader',
            name='date_time_issued',
            field=models.DateTimeField(default=datetime.datetime(2021, 3, 11, 13, 55, 30, 556161)),
        ),
    ]
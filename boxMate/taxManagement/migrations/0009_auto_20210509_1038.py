# Generated by Django 2.2.6 on 2021-05-09 08:38

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taxManagement', '0008_merge_20210506_1247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoiceheader',
            name='date_time_issued',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 9, 10, 38, 42, 454514)),
        ),
    ]

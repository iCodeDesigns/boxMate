# Generated by Django 2.2.6 on 2021-03-01 09:36

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taxManagement', '0007_auto_20210301_0932'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoiceheader',
            name='date_time_issued',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2021, 3, 1, 9, 36, 47, 632762), null=True),
        ),
    ]

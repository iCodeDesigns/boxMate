# Generated by Django 2.2.6 on 2021-02-11 08:19

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taxManagement', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoiceheader',
            name='date_time_issued',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2021, 2, 11, 8, 19, 19, 143658), null=True),
        ),
    ]
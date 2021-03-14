# Generated by Django 2.2.6 on 2021-03-11 13:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taxManagement', '0004_auto_20210311_1354'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoiceline',
            name='currencySold',
            field=models.CharField(blank=True, help_text='Currency code used from ISO 4217.', max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='invoiceheader',
            name='date_time_issued',
            field=models.DateTimeField(default=datetime.datetime(2021, 3, 11, 13, 54, 18, 603412)),
        ),
    ]
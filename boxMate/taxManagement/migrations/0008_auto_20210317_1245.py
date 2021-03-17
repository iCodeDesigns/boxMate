# Generated by Django 2.2.6 on 2021-03-17 10:45

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('currencies', '0006_increase_name_max_length'),
        ('taxManagement', '0007_auto_20210317_1241'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoiceline',
            name='currencySold',
            field=models.ForeignKey(default='EGP', on_delete=django.db.models.deletion.CASCADE, to='currencies.Currency'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='invoiceheader',
            name='date_time_issued',
            field=models.DateTimeField(default=datetime.datetime(2021, 3, 17, 12, 44, 58, 753069)),
        ),
    ]

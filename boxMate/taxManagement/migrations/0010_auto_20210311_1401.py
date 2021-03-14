# Generated by Django 2.2.6 on 2021-03-11 14:01

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('taxManagement', '0009_auto_20210311_1356'),
    ]

    operations = [
        migrations.AddField(
            model_name='maintable',
            name='currency_sold',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='invoiceheader',
            name='date_time_issued',
            field=models.DateTimeField(default=datetime.datetime(2021, 3, 11, 14, 1, 10, 926036)),
        ),
        migrations.AlterField(
            model_name='invoiceline',
            name='currencySold',
            field=models.ForeignKey(default='EGP', on_delete=django.db.models.deletion.CASCADE, to='currencies.Currency'),
            preserve_default=False,
        ),
    ]
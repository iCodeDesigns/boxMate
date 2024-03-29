# Generated by Django 2.2.6 on 2021-05-06 14:50

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('taxManagement', '0009_auto_20210506_1649'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoiceheader',
            name='date_time_issued',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 6, 16, 50, 1, 753945)),
        ),
        migrations.AlterField(
            model_name='invoiceheader',
            name='taxpayer_activity_code',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='issuer.IssuerActivityCode'),
        ),
    ]

# Generated by Django 2.2.6 on 2021-04-28 12:26

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('taxManagement', '0004_auto_20210428_1406'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoiceheader',
            name='date_time_issued',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 28, 14, 26, 22, 220686)),
        ),
        migrations.AlterField(
            model_name='invoiceheader',
            name='receiver',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver_val', to='issuer.Receiver'),
        ),
    ]

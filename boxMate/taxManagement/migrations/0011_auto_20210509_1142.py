# Generated by Django 2.2.6 on 2021-05-09 09:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taxManagement', '0010_auto_20210509_1115'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoiceheader',
            name='date_time_issued',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 9, 11, 42, 6, 527958)),
        ),
    ]

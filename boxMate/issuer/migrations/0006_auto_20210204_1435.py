# Generated by Django 2.2.6 on 2021-02-04 14:35

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('issuer', '0005_auto_20210204_1434'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issuertax',
            name='start_date',
            field=models.DateField(blank=True, default=datetime.datetime(2021, 2, 4, 14, 35, 4, 745003, tzinfo=utc), null=True),
        ),
    ]

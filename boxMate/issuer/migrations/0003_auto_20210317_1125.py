# Generated by Django 2.2.6 on 2021-03-17 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issuer', '0002_auto_20210315_1007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receiver',
            name='reg_num',
            field=models.CharField(max_length=20, verbose_name='reg_number'),
        ),
    ]

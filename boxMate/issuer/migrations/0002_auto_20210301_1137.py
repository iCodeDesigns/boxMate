# Generated by Django 2.2.6 on 2021-03-01 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issuer', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issuer',
            name='reg_num',
            field=models.CharField(max_length=20, unique=True, verbose_name='reg_number'),
        ),
    ]

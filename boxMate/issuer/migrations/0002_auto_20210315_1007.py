# Generated by Django 2.2.6 on 2021-03-15 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issuer', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issuertax',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='issuertax',
            name='last_updated_at',
            field=models.DateField(blank=True, null=True),
        ),
    ]
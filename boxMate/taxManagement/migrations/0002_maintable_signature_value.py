# Generated by Django 2.2.6 on 2021-02-04 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taxManagement', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='maintable',
            name='signature_value',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]

# Generated by Django 2.2.6 on 2021-03-01 08:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('codes', '0001_initial'),
        ('issuer', '0003_auto_20210228_0844'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='issuertax',
            name='tax_type',
        ),
        migrations.AddField(
            model_name='issuertax',
            name='issuer_sub_tax',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='issuer_sub_tax', to='codes.TaxSubtypes'),
        ),
    ]

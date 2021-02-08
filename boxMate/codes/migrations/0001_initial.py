# Generated by Django 2.2.6 on 2021-02-07 12:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityType',
            fields=[
                ('code', models.CharField(max_length=6, primary_key=True, serialize=False)),
                ('desc_en', models.TextField(blank=True, null=True)),
                ('desc_ar', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CountryCode',
            fields=[
                ('code', models.CharField(max_length=4, primary_key=True, serialize=False)),
                ('desc_en', models.TextField(blank=True, null=True)),
                ('desc_ar', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TaxTypes',
            fields=[
                ('code', models.CharField(max_length=4, primary_key=True, serialize=False)),
                ('desc_en', models.CharField(max_length=50)),
                ('desc_ar', models.CharField(max_length=50)),
                ('is_taxable', models.BooleanField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UnitType',
            fields=[
                ('code', models.CharField(max_length=5, primary_key=True, serialize=False)),
                ('desc_en', models.TextField(blank=True, null=True)),
                ('desc_ar', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TaxSubtypes',
            fields=[
                ('code', models.CharField(max_length=4, primary_key=True, serialize=False)),
                ('desc_en', models.CharField(max_length=50)),
                ('desc_ar', models.CharField(max_length=50)),
                ('taxtype_reference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='codes.TaxTypes')),
            ],
        ),
    ]

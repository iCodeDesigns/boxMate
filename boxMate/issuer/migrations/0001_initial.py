# Generated by Django 2.2.6 on 2021-03-11 13:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('codes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Issuer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('B', 'business'), ('P', 'natural person'), ('F', 'foreigner')], default='B', max_length=8)),
                ('reg_num', models.CharField(max_length=20, unique=True, verbose_name='reg_number')),
                ('name', models.CharField(blank=True, max_length=50, null=True, verbose_name='issuer name')),
                ('client_id', models.CharField(blank=True, max_length=50, null=True)),
                ('clientSecret1', models.CharField(blank=True, max_length=50, null=True)),
                ('clientSecret2', models.CharField(blank=True, max_length=50, null=True)),
                ('created_at', models.DateField(auto_now_add=True, null=True)),
                ('last_updated_at', models.DateField(auto_now=True, null=True)),
                ('activity_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='codes.ActivityType')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Issuer_created_by', to=settings.AUTH_USER_MODEL)),
                ('last_updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Issuer_last_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Receiver',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('B', 'business'), ('P', 'natural person'), ('F', 'foreigner')], default='B', max_length=8)),
                ('reg_num', models.CharField(max_length=8, verbose_name='reg_number')),
                ('name', models.CharField(blank=True, max_length=50, null=True, verbose_name='reciever name')),
                ('created_at', models.DateField(auto_now_add=True, null=True)),
                ('last_updated_at', models.DateField(auto_now=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Receiver_created_by', to=settings.AUTH_USER_MODEL)),
                ('issuer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='issuer.Issuer')),
                ('last_updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='IssuerTax',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(blank=True, default=django.utils.timezone.now, null=True)),
                ('end_date', models.DateField(auto_now_add=True, null=True)),
                ('is_enabled', models.BooleanField()),
                ('created_at', models.DateField(auto_now_add=True, null=True)),
                ('last_updated_at', models.DateField(auto_now=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='issuer_tax_created_by', to=settings.AUTH_USER_MODEL)),
                ('issuer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='issuer_tax', to='issuer.Issuer')),
                ('issuer_sub_tax', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='issuer_sub_tax', to='codes.TaxSubtypes')),
                ('last_updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='issuer_tax_last_update_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='IssuerOracleDB',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.CharField(max_length=20)),
                ('port_number', models.CharField(max_length=10)),
                ('service_number', models.CharField(max_length=10)),
                ('username', models.CharField(max_length=30)),
                ('password', models.CharField(max_length=100)),
                ('database_name', models.CharField(max_length=50)),
                ('is_active', models.BooleanField(default=False)),
                ('issuer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='issuer.Issuer')),
            ],
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('branch_id', models.CharField(max_length=10)),
                ('governate', models.CharField(blank=True, max_length=50, null=True)),
                ('regionCity', models.CharField(blank=True, max_length=50, null=True)),
                ('street', models.CharField(blank=True, max_length=120, null=True)),
                ('buildingNumber', models.CharField(blank=True, max_length=120, null=True)),
                ('postalCode', models.CharField(blank=True, max_length=20, null=True)),
                ('floor', models.CharField(blank=True, max_length=10, null=True)),
                ('room', models.CharField(blank=True, max_length=10, null=True)),
                ('landmark', models.CharField(blank=True, max_length=120, null=True)),
                ('additionalInformation', models.CharField(blank=True, max_length=250, null=True)),
                ('created_at', models.DateField(auto_now_add=True, null=True)),
                ('last_updated_at', models.DateField(auto_now=True, null=True)),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='codes.CountryCode')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='address_created_by', to=settings.AUTH_USER_MODEL)),
                ('issuer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='issuer_addresses', to='issuer.Issuer')),
                ('last_updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('receiver', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rec_addresses', to='issuer.Receiver')),
            ],
        ),
    ]
